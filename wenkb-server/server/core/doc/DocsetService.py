import uuid
from datetime import datetime
from server.db.DbManager import session_scope
from sqlalchemy import delete
from server.model.orm_doc import DocsetInfo, DocmtVersion, DocmtInfo
from server.model.orm_knb import Dataset, ReposInfo
from server.model.entity_doc import DocsetInfo as DocsetInfoEntity
from server.exception.exception import BaseBusiException
from server.core.knb.DatasetService import DatasetService

class DocsetService():
  datasetService = DatasetService()
  # 根据文档集id与用户id查询文档集信息，带权限的信息
  def select_by_set_id_and_user_id(self, setId:str, userId:str):
    with session_scope() as session:
      orm = session.query(DocsetInfo).where(
        DocsetInfo.setId == setId,
        (DocsetInfo.crtUser == userId) | (DocsetInfo.authRang == 'pblc')
      ).first()
      if orm is None: return None
      docsetInfo = DocsetInfoEntity().copy_from_dict(orm.to_dict())
      docsetInfo.optAuth = 'alter' if orm.crtUser == userId else 'visit'
      return docsetInfo
  # 查询用户的文档集列表
  def select_list_by_user_id(self, userId:str):
    with session_scope(True) as session:
      orms = session.query(DocsetInfo).where(
        (DocsetInfo.crtUser == userId) | (DocsetInfo.authRang == 'pblc')
      ).order_by(DocsetInfo.crtTm.desc()).all()
      result = []
      for orm in orms:
        entity = DocsetInfoEntity().copy_from_dict(orm.to_dict())
        entity.optAuth = 'alter' if orm.crtUser == userId else 'visit'
        result.append(entity)
      return result

  def remove_document_set_by_id(self, setId: str):
    with session_scope() as session:
      doc_ids = session.scalars(
        session.query(DocmtInfo.docId).where(DocmtInfo.setId == setId).statement
      ).all()
      if doc_ids:
        session.execute(delete(DocmtVersion).where(DocmtVersion.docId.in_(doc_ids)))
        session.execute(delete(DocmtInfo).where(DocmtInfo.docId.in_(doc_ids)))
      session.execute(delete(DocsetInfo).where(DocsetInfo.setId == setId))

  def remove_document_by_id(self, docId: str):
    with session_scope() as session:
      session.execute(delete(DocmtVersion).where(DocmtVersion.docId == docId))
      session.execute(delete(DocmtInfo).where(DocmtInfo.docId == docId))
  
  # 将文档发布到数据集中
  def add_to_dataset(self, reposId:str, docId:str, userId:str):
    with session_scope() as session:
      info = session.get(DocmtInfo, docId)
      if (info is None):
        raise BaseBusiException('文档不存在或被删除')
      repository = session.get(ReposInfo, reposId)
      if repository is None:
        raise BaseBusiException('知识库不存在或已被删除')
      if repository.crtUser != userId and repository.authRang != 'pblc':
        raise BaseBusiException('您没有权限向该知识库导入文档', status_code=403)
      # 创建版本
      verId = str(uuid.uuid4()).replace('-', '')
      now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      version = DocmtVersion(
        verId=verId,
        docId=info.docId,
        setId=info.setId,
        docTtl=info.docTtl,
        docTyp=info.docTyp,
        docCntnt=info.docCntnt,
        crtUser=userId,
        crtTm=now
      )
      session.add(version)

      # 查询是否已经添加到该知识库
      dataset = session.query(Dataset).where(Dataset.reposId==reposId, Dataset.docId==docId).first()
      dtsetId = str(uuid.uuid4()).replace('-', '')
      enbSts = 'une'
      if (dataset is not None):
        dtsetId = dataset.dtsetId
        enbSts = dataset.enbSts
        self.datasetService.removeDatasetExtendsByIdAndTypes(reposId=reposId, dtsetId=dtsetId, session=session)
      # 创建数据集与版本关联起来
      
      dataset = Dataset(
        dtsetId = dtsetId,
        reposId = reposId,
        dtsetTyp = 'dcmt', # 暂时默认只支持文本
        dtsetNm = version.docTtl,
        docId = docId,
        docVerId = verId,
        fileTyp = 'html' if version.docTyp == 'rt' else 'md',
        idxSts = 'new',
        prcsSts = 'nobd',
        qaSts = 'nobd',
        tpltSts = 'nobd',
        enbSts = enbSts, # enb 已启用，une 未启用
        crtUser = userId,
        crtTm = version.crtTm,
        fileNm = version.docTtl
      )
      session.merge(dataset)
