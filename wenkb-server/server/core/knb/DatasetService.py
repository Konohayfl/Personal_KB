import json
import os
import uuid
from langchain_core.documents import Document
from server.db.DbManager import session_scope
from sqlalchemy import delete, select
from server.model.orm_knb import Dataset, DatasetChunk, ReposQuest, DatasetPrecis, DatasetTriplet
from server.model.entity_knb import DatasetChunk as DatasetChunkEntity, DatasetPrecis as DatasetPrecisEntity, DatasetTriplet as DatasetTripletEntity
from server.core.tools.repos_vector_db import vector_get, vector_update_document, vector_delete, vector_add_texts
from server.core.tools.dataset_to_metadata import precis_to_metadata, triplet_to_metadata

class DatasetService():
  # 删除数据集相关内容：分段，摘要，QA，索引等
  def removeDatasetExtendsByIdAndTypes(
    self,
    reposId: str,
    dtsetId: str,
    session,
    types: list = None,
    include_manual: bool = False
  ):
    if types is None:
      types = ['index', 'precis', 'qanswer', 'triplet']
    ids = []
    if ('index' in types):
      chunks = session.scalars(select(DatasetChunk.chkId).where(DatasetChunk.dtsetId == dtsetId)).all()
      ids.extend(chunks)
      # 删除数据集分片
      session.execute(delete(DatasetChunk).where(DatasetChunk.dtsetId == dtsetId))
    if ('precis' in types):
      precis_query = select(DatasetPrecis.prcsId).where(DatasetPrecis.dtsetId == dtsetId)
      if not include_manual:
        precis_query = precis_query.where(DatasetPrecis.prcsSrc == 'ai')
      ids.extend(session.scalars(precis_query).all())
      # 删除摘要
      precis_delete = delete(DatasetPrecis).where(DatasetPrecis.dtsetId == dtsetId)
      if not include_manual:
        precis_delete = precis_delete.where(DatasetPrecis.prcsSrc == 'ai')
      session.execute(precis_delete)
    if ('qanswer' in types):
      quest_query = select(ReposQuest.qstId).where(ReposQuest.dtsetId == dtsetId)
      if not include_manual:
        quest_query = quest_query.where(ReposQuest.qstSrc == 'ai')
      ids.extend(session.scalars(quest_query).all())
      # 删除Q&A
      quest_delete = delete(ReposQuest).where(ReposQuest.dtsetId == dtsetId)
      if not include_manual:
        quest_delete = quest_delete.where(ReposQuest.qstSrc == 'ai')
      session.execute(quest_delete)
    if ('triplet' in types):
      triplet_query = select(DatasetTriplet.tpltId).where(DatasetTriplet.dtsetId == dtsetId)
      if not include_manual:
        triplet_query = triplet_query.where(DatasetTriplet.tpltSrc == 'ai')
      ids.extend(session.scalars(triplet_query).all())
      # 删除三元组
      triplet_delete = delete(DatasetTriplet).where(DatasetTriplet.dtsetId == dtsetId)
      if not include_manual:
        triplet_delete = triplet_delete.where(DatasetTriplet.tpltSrc == 'ai')
      session.execute(triplet_delete)
    
    # 删除向量库的内容
    if (len(ids) > 0):
      vector_delete(reposId=reposId, ids=ids)

  def removeDatasetById(self, dtsetId: str):
    file_path = None
    file_type = None
    with session_scope() as session:
      orm = session.get(Dataset, dtsetId)
      if (orm is None):
        return
      reposId = orm.reposId
      file_path = orm.filePath
      file_type = orm.fileTyp
      self.removeDatasetExtendsByIdAndTypes(
        reposId=reposId,
        dtsetId=dtsetId,
        session=session,
        include_manual=True
      )
      # 删除数据集
      session.delete(orm)
    if file_path and file_type != 'link' and os.path.isfile(file_path):
      try:
        os.remove(file_path)
      except OSError:
        # 数据库和向量索引已经完成清理，文件清理可以由运维任务重试。
        pass

  # types: [ 'index', 'precis', 'qanswer', 'triplet' ]
  def reindexDatasetByIdAndTypes(self, dtsetId: str, types: list):
    with session_scope() as session:
      orm = session.get(Dataset, dtsetId)
      if (orm is None):
        return
      reposId = orm.reposId
      if ('index' in types):
        orm.idxSts = 'new'
      if ('precis' in types):
        orm.prcsSts = 'new'
      if ('qanswer' in types):
        orm.qaSts = 'new'
      if ('triplet' in types):
        orm.tpltSts = 'new'

      session.merge(orm) # 重置状态
      self.removeDatasetExtendsByIdAndTypes(reposId=reposId, dtsetId=dtsetId, types=types, session=session)

  def get_chunk_vector_text(self, content:str, assist: str = None):
    if (assist is None or len(assist) == 0):
      return content
    d = {
      'content': content,
      'assist': assist
    }
    return json.dumps(d, ensure_ascii=False)
  # 修改数据集分片内容 ，return部分暂时都不处理
  def modifyChunkContent(self, datasetChunk: DatasetChunkEntity):
    chkId = datasetChunk.chkId
    chkCntnt = datasetChunk.chkCntnt
    chkAsst = datasetChunk.chkAsst
    with session_scope() as session:
      orm = session.get(DatasetChunk, chkId)
      if (orm is None):
        return
      if (orm.chkCntnt == chkCntnt and orm.chkAsst == chkAsst):
        return
      reposId = orm.reposId
      result = vector_get(reposId=reposId, ids=chkId, limit=1) # { ids: [], metadatas: [], documents: [] }
      isNew = len(result) == 0
      if (isNew):
        orm.chkCntnt = chkCntnt
        orm.chkAsst = chkAsst
        session.merge(orm)
        return
      else:
        text = self.get_chunk_vector_text(content=chkCntnt, assist=chkAsst)
        vector_update_document(reposId=reposId, document_id=chkId, document=Document(page_content=text, metadata=result['metadatas'][0])) # 更新到向量库
        # 更新到数据库
        orm.chkCntnt = chkCntnt
        orm.chkAsst = chkAsst
        session.merge(orm)

  def removeChunkById(self, chkId: str):
    with session_scope() as session:
      orm = session.get(DatasetChunk, chkId)
      if (orm is None):
        return
      vector_delete(reposId=orm.reposId, ids=[chkId])
      # 删除数据库
      session.delete(orm)
  
  def addPrecis(self, datasetPrecis: DatasetPrecisEntity):
    datasetPrecis.prcsId = str(uuid.uuid4()).replace('-', '')
    with session_scope() as session:
      session.add(DatasetPrecis().copy_from_dict(vars(datasetPrecis)))
      dtsetId = datasetPrecis.dtsetId
      if (dtsetId is not None):
        dataset = session.get(Dataset, dtsetId)
      # 添加到向量数据库
      text = datasetPrecis.prcsCntnt
      metadata = precis_to_metadata(precis=datasetPrecis, dataset=dataset)
      vector_add_texts(reposId=datasetPrecis.reposId, texts=[text], metadatas=[metadata], ids=[datasetPrecis.prcsId])
    return datasetPrecis
  # 修改数据集摘要内容 ，return部分暂时都不处理
  def modifyPrecisContent(self, datasetPrecis: DatasetPrecisEntity):
    prcsId = datasetPrecis.prcsId
    prcsCntnt = datasetPrecis.prcsCntnt

    with session_scope() as session:
      orm = session.get(DatasetPrecis, prcsId)
      if (orm is None):
        return
      if (orm.prcsCntnt == prcsCntnt):
        return
      reposId = orm.reposId
      result = vector_get(reposId=reposId, ids=prcsId, limit=1) # { ids: [], metadatas: [], documents: [] }
      isNew = len(result) == 0
      if (isNew):
        orm.prcsCntnt = prcsCntnt
        session.merge(orm)
        return
      else:
        text = prcsCntnt
        vector_update_document(reposId=reposId, document_id=prcsId, document=Document(page_content=text, metadata=result['metadatas'][0])) # 更新到向量库
        # 更新到数据库
        orm.prcsCntnt = prcsCntnt
        session.merge(orm)

  def removePrecisById(self, prcsId: str):
    with session_scope() as session:
      orm = session.get(DatasetPrecis, prcsId)
      if (orm is None):
        return
      vector_delete(reposId=orm.reposId, ids=[prcsId])
      # 删除数据库
      session.delete(orm)


  def get_triplet_vector_text(self, subject:str, predicate:str, object:str):
    return f'({subject},{predicate},{object})'

  def addTriplet(self, datasetTriplet: DatasetTripletEntity):
    datasetTriplet.tpltId = str(uuid.uuid4()).replace('-', '')
    with session_scope() as session:
      session.add(DatasetTriplet().copy_from_dict(vars(datasetTriplet)))
      dtsetId = datasetTriplet.dtsetId
      if (dtsetId is not None):
        dataset = session.get(Dataset, dtsetId)
      # 添加到向量数据库
      text = self.get_triplet_vector_text(subject=datasetTriplet.tpltSbjct, predicate=datasetTriplet.tpltPrdct, object=datasetTriplet.tpltObjct)
      metadata = triplet_to_metadata(triplet=datasetTriplet, dataset=dataset)
      vector_add_texts(reposId=datasetTriplet.reposId, texts=[text], metadatas=[metadata], ids=[datasetTriplet.tpltId])
    return datasetTriplet
  
  # 修改数据集三元组 ，return部分暂时都不处理
  def modifyTriplet(self, datasetTriplet: DatasetTripletEntity):
    tpltId = datasetTriplet.tpltId
    with session_scope() as session:
      orm = session.get(DatasetTriplet, tpltId)
      if (orm is None):
        return
      reposId = orm.reposId
      result = vector_get(reposId=reposId, ids=tpltId, limit=1) # { ids: [], metadatas: [], documents: [] }
      isNew = len(result) == 0
      if (isNew):
        orm.copy_from_dict(datasetTriplet.to_dict())
        session.merge(orm)
        return
      else:
        text = self.get_triplet_vector_text(subject=datasetTriplet.tpltSbjct, predicate=datasetTriplet.tpltPrdct, object=datasetTriplet.tpltObjct)
        vector_update_document(reposId=reposId, document_id=tpltId, document=Document(page_content=text, metadata=result['metadatas'][0])) # 更新到向量库
        # 更新到数据库
        orm.copy_from_dict(datasetTriplet.to_dict())
        session.merge(orm)

  def removeTripletById(self, tpltId: str):
    with session_scope() as session:
      orm = session.get(DatasetTriplet, tpltId)
      if (orm is None):
        return
      vector_delete(reposId=orm.reposId, ids=[tpltId])
      # 删除数据库
      session.delete(orm)
