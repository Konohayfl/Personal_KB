import json
import uuid
from server.db.DbManager import session_scope
from langchain_core.documents import Document
from sqlalchemy import delete, select
from server.model.orm_knb import (
  ReposInfo, ReposQuest, Dataset, DatasetCtlg, DatasetChunk,
  DatasetPrecis, DatasetTriplet, DatasetIndexError, ChatInfo,
  ChatMesg, ChatMesgQuote, SrchHist, ReposSetting
)
from server.model.entity_knb import ReposInfo as ReposInfoEntity, ReposQuest as ReposQuestEntity, ReposSetting as ReposSettingEntity
from server.core.tools.repos_vector_db import (
  vector_get, vector_update_document, vector_delete, vector_add_texts,
  vector_delete_collection
)
from server.core.tools.dataset_to_metadata import quest_to_metadata

class ReposService():
  def get_quest_vector_text(self, question:str, answer: str = None):
    d = {
      'question': question,
      'answer': answer
    }
    return json.dumps(d, ensure_ascii=False)
  
  # 根据知识库id与用户id查询知识库信息，带权限的信息
  def select_by_repos_id_and_user_id(self, reposId:str, userId:str):
    with session_scope() as session:
      orm = session.query(ReposInfo).where(
        ReposInfo.reposId == reposId,
        (ReposInfo.crtUser == userId) | (ReposInfo.authRang == 'pblc')
      ).first()
      if orm is None: return None
      reposInfo = ReposInfoEntity().copy_from_dict(orm.to_dict())
      reposInfo.optAuth = 'alter' if orm.crtUser == userId else 'visit'
      return reposInfo
  # 查询用户的知识库列表
  def select_list_by_user_id(self, userId:str):
    with session_scope(True) as session:
      orms = session.query(ReposInfo).where(
        (ReposInfo.crtUser == userId) | (ReposInfo.authRang == 'pblc')
      ).order_by(ReposInfo.crtTm.desc()).all()
      result = []
      for orm in orms:
        entity = ReposInfoEntity().copy_from_dict(orm.to_dict())
        entity.optAuth = 'alter' if orm.crtUser == userId else 'visit'
        result.append(entity)
      return result

  def remove_repository_by_id(self, reposId: str):
    # 先删除向量集合，失败时保留关系库数据，方便整体重试。
    vector_delete_collection(reposId)
    with session_scope() as session:
      repository = session.get(ReposInfo, reposId)
      if repository is None:
        return
      session.execute(delete(ChatMesgQuote).where(ChatMesgQuote.reposId == reposId))
      session.execute(delete(ChatMesg).where(ChatMesg.reposId == reposId))
      session.execute(delete(ChatInfo).where(ChatInfo.reposId == reposId))
      session.execute(delete(SrchHist).where(SrchHist.reposId == reposId))
      session.execute(delete(ReposQuest).where(ReposQuest.reposId == reposId))
      dataset_ids = session.scalars(
        select(Dataset.dtsetId).where(Dataset.reposId == reposId)
      ).all()
      if dataset_ids:
        session.execute(delete(DatasetIndexError).where(DatasetIndexError.dtsetId.in_(dataset_ids)))
        session.execute(delete(DatasetChunk).where(DatasetChunk.dtsetId.in_(dataset_ids)))
        session.execute(delete(DatasetPrecis).where(DatasetPrecis.dtsetId.in_(dataset_ids)))
        session.execute(delete(DatasetTriplet).where(DatasetTriplet.dtsetId.in_(dataset_ids)))
      session.execute(delete(Dataset).where(Dataset.reposId == reposId))
      session.execute(delete(DatasetCtlg).where(DatasetCtlg.reposId == reposId))
      session.execute(delete(ReposSetting).where(ReposSetting.reposId == reposId))
      session.delete(repository)
  
  def add_repos_quest(self, reposQuest: ReposQuestEntity):
    reposQuest.qstId = str(uuid.uuid4()).replace('-', '')
    with session_scope() as session:
      session.add(ReposQuest().copy_from_dict(vars(reposQuest)))
      dtsetId = reposQuest.dtsetId
      if (dtsetId is not None):
        dataset = session.get(Dataset, dtsetId)
      # 添加到向量数据库
      text = self.get_quest_vector_text(question=reposQuest.qstQuest, answer=reposQuest.qstAswr)
      metadata = quest_to_metadata(quest=reposQuest, dataset=dataset)
      vector_add_texts(reposId=reposQuest.reposId, texts=[text], metadatas=[metadata], ids=[reposQuest.qstId])
    return reposQuest

  # 修改问答对
  def edit_repos_quest(self, reposQuest: ReposQuestEntity):
    with session_scope() as session:
      session.merge(ReposQuest().copy_from_dict(vars(reposQuest)))
      reposId = reposQuest.reposId
      qstId = reposQuest.qstId
      # 修改向量库
      result = vector_get(reposId=reposId, ids=qstId, limit=1) # { ids: [], metadatas: [], documents: [] }
      isNew = len(result) == 0
      if (isNew): # 暂时不管
        return
      text = self.get_quest_vector_text(question=reposQuest.qstQuest, answer=reposQuest.qstAswr)
      vector_update_document(reposId=reposId, document_id=qstId, document=Document(page_content=text, metadata=result['metadatas'][0])) # 更新到向量库
  
  # 删除问答对
  def remove_repos_quest(self, qstId: str):
    with session_scope() as session:
      orm = session.get(ReposQuest, qstId)
      if (orm is None):
        return
      vector_delete(reposId=orm.reposId, ids=[qstId])
      # 删除数据库
      session.delete(orm)

  # 获取知识库设置
  def get_repos_setting(self, reposId: str):
    with session_scope(True) as session:
      orm = session.get(ReposSetting, reposId)
      if (orm is not None):
        return ReposSettingEntity().copy_from_dict(orm.to_dict())
    return ReposSettingEntity(reposId=reposId)
