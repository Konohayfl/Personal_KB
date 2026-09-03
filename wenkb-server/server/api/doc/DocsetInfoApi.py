import uuid
from fastapi import FastAPI, Request
from server.db.DbManager import session_scope
from server.api.BaseApi import BaseApi
from sqlalchemy import select, update
from sqlalchemy.orm import defer
from datetime import datetime
from server.model.form_doc import DocmtToDatasetForm
from server.model.orm_doc import DocsetInfo, DocmtInfo, DocmtVersion
from server.model.orm_knb import Dataset
from server.model.entity_doc import DocsetInfo as DocsetInfoEntity, DocmtInfo as DocmtInfoEntity
from server.utils.websocketutils import WebsocketManager
from server.core.doc.DocsetService import DocsetService
from server.exception.exception import BaseBusiException

class DocsetInfoApi(BaseApi):
  docsetService = DocsetService()
  def __init__(self, app: FastAPI, manager: WebsocketManager = None):
    BaseApi.__init__(self)

    def require_docset_access(setId: str, request: Request, owner: bool = False):
      userId = self.getUserId(request)
      with session_scope(True) as session:
        orm = session.get(DocsetInfo, setId)
        if (orm is None):
          raise BaseBusiException('文档集不存在或已被删除', status_code=404)
        if (orm.crtUser != userId and orm.authRang != 'pblc'):
          raise BaseBusiException('您没有权限访问该文档集', status_code=403)
        if (owner and orm.crtUser != userId):
          raise BaseBusiException('您没有权限修改该文档集', status_code=403)
        docset = DocsetInfoEntity().copy_from_dict(orm.to_dict())
        docset.optAuth = 'alter' if orm.crtUser == userId else 'visit'
        return docset

    def require_document_access(docId: str, request: Request, owner: bool = False):
      userId = self.getUserId(request)
      with session_scope(True) as session:
        orm = session.get(DocmtInfo, docId)
        if (orm is None):
          raise BaseBusiException('文档不存在或已被删除', status_code=404)
        docset = session.get(DocsetInfo, orm.setId)
        if (docset is None):
          raise BaseBusiException('文档集不存在或已被删除', status_code=404)
        if (docset.crtUser != userId and docset.authRang != 'pblc'):
          raise BaseBusiException('您没有权限访问该文档', status_code=403)
        if (owner and docset.crtUser != userId):
          raise BaseBusiException('您没有权限修改该文档', status_code=403)
        return orm, docset

    # 获取单个文档集
    @app.get('/doc/docset/{id}')
    def getDocumentSet(id: str, request: Request):
      return self.success(require_docset_access(id, request))
    
    # 修改名称
    @app.put('/doc/docset/name')
    def editDocumentSetName(docsetInfo: DocsetInfoEntity, request: Request):
      setId = docsetInfo.setId
      require_docset_access(setId, request, owner=True)
      with session_scope() as session:
        orm = session.get(DocsetInfo, setId)
        orm.setNm = docsetInfo.setNm
        session.merge(orm)
      return self.success()
    
    # 修改介绍
    @app.put('/doc/docset/desc')
    def editDocumentSetDesc(docsetInfo: DocsetInfoEntity, request: Request):
      setId = docsetInfo.setId
      require_docset_access(setId, request, owner=True)
      with session_scope() as session:
        orm = session.get(DocsetInfo, setId)
        orm.setDesc = docsetInfo.setDesc
        session.merge(orm)
      return self.success()
    
    # 修改权限
    @app.put('/doc/docset/auth/range')
    def editDocumentSetAuthRange(docsetInfo: DocsetInfoEntity, request: Request):
      setId = docsetInfo.setId
      authRang = docsetInfo.authRang
      require_docset_access(setId, request, owner=True)
      with session_scope() as session:
        orm = session.get(DocsetInfo, setId)
        if (orm.authRang == authRang):
          return self.success()
        orm.authRang = authRang
        session.merge(orm)
        # if (authRang == 'prvt' or authRang == 'pblc'): # 需要删除团队信息
        #   session.query(DocsetTeam).filter(DocsetTeam.setId == setId).delete()
      return self.success()

    # 查询文档集列表
    @app.post('/doc/docset/list')
    def documentSetList(request:Request):
      return self.success(self.docsetService.select_list_by_user_id(self.getUserId(request)))
    
    # 查询文档集列表
    @app.post('/doc/docset/my/list')
    def documentSetList(request:Request):
      return self.success(self.docsetService.select_list_by_user_id(self.getUserId(request)))
    
    # 新增文档集
    @app.post('/doc/docset')
    def addDocumentSet(docsetInfo: DocsetInfoEntity, request: Request):
      # setId='' setNm='123456' setDesc='' setIcon=None crtUser=None authRang=None
      docsetInfo.setId = self.getPk()
      docsetInfo.crtTm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      docsetInfo.crtUser = self.getUserId(request=request)
      if (docsetInfo.authRang is None):
        docsetInfo.authRang = 'prvt'
      orm = DocsetInfo().copy_from_dict(vars(docsetInfo))
      with session_scope() as session:
        session.add(orm)
      return self.success(docsetInfo)
    
    # 修改文档集
    @app.put('/doc/docset')
    def editDocumentSet(docsetInfo:DocsetInfoEntity, request: Request):
      # setId='' setNm='123456' setDesc='' setIcon=None crtUser=None authRang=None
      setId = docsetInfo.setId
      require_docset_access(setId, request, owner=True)
      with session_scope() as session:
        orm = session.get(DocsetInfo, setId)
        orm.setNm = docsetInfo.setNm
        orm.setDesc = docsetInfo.setDesc
        orm.setIcon = docsetInfo.setIcon
        orm.authRang = docsetInfo.authRang
        session.merge(orm)
      return self.success()

    # 删除文档集
    @app.delete('/doc/docset/{id}')
    def removeDocumentSet(id:str, request: Request):
      # setId='' setNm='123456' setDesc='' setIcon=None crtUser=None authRang=None
      docset = self.docsetService.select_by_set_id_and_user_id(
        id, self.getUserId(request)
      )
      if docset is None or docset.optAuth != 'alter':
        raise BaseBusiException('您没有权限删除该文档集', status_code=403)
      self.docsetService.remove_document_set_by_id(id)
      return self.success()
    
    # 查询文档集中的文档列表
    @app.post('/doc/document/list/{id}')
    def documentList(id: str, request: Request):
      require_docset_access(id, request)
      stmt = select(DocmtInfo).where(DocmtInfo.setId==id).options(defer(DocmtInfo.docCntnt)).order_by(DocmtInfo.crtTm.asc())
      list = []
      with session_scope(True) as session:
        for row in session.scalars(stmt):
          list.append(row)
      return self.success(list)
    
    # 新增文档
    @app.post('/doc/document')
    def addDocument(docmtInfo: DocmtInfoEntity, request: Request):
      docmtInfo.docId = self.getPk()
      docmtInfo.crtTm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      docmtInfo.updTm = docmtInfo.crtTm
      docmtInfo.crtUser = self.getUserId(request=request)
      docPid = docmtInfo.docPid
      docPath = '/' + docmtInfo.docId
      with session_scope() as session:
        require_docset_access(docmtInfo.setId, request, owner=True)
        if (docPid is not None):
          porm = session.get(DocmtInfo, docPid)
          if (porm is None):
            raise BaseBusiException('上级文档不存在或被删除')
          docPath = porm.docPath + docPath
        docmtInfo.docPath = docPath
        orm = DocmtInfo().copy_from_dict(vars(docmtInfo))
        session.add(orm)
      return self.success(docmtInfo)
    
    # 修改文档
    @app.put('/doc/document')
    def editDocument(docmtInfo: DocmtInfoEntity, request: Request):
      docId = docmtInfo.docId
      require_document_access(docId, request, owner=True)
      with session_scope() as session:
        orm = session.get(DocmtInfo, docId)
        orm.docTtl = docmtInfo.docTtl
        session.merge(orm)
      return self.success()

    # 删除文档
    @app.delete('/doc/document/{id}')
    def removeDocument(id:str, request: Request):
      with session_scope() as session:
        orm = session.get(DocmtInfo, id)
        if orm is None:
          return self.success()
        docset = session.get(DocsetInfo, orm.setId)
        if docset is None or docset.crtUser != self.getUserId(request):
          raise BaseBusiException('您没有权限删除该文档', status_code=403)
      self.docsetService.remove_document_by_id(id)
      return self.success()
    
    # 获取单个文档
    @app.get('/doc/document/{id}')
    def getDocument(id: str, request: Request):
      require_document_access(id, request)
      with session_scope(True) as session:
        orm = session.get(DocmtInfo, id)
      return self.success(orm)
    
    # 修改内容
    @app.put('/doc/document/content')
    def editDocumentContent(docmtInfo: DocmtInfoEntity, request: Request):
      docId = docmtInfo.docId
      docCntnt = docmtInfo.docCntnt
      require_document_access(docId, request, owner=True)
      with session_scope() as session:
        orm = session.get(DocmtInfo, docId)
        if orm is None:
          raise BaseBusiException('文档不存在或已被删除', status_code=404)
        if orm.crtUser != self.getUserId(request):
          raise BaseBusiException('您没有权限修改该文档', status_code=403)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        version = DocmtVersion(
          verId=str(uuid.uuid4()).replace('-', ''),
          docId=orm.docId,
          setId=orm.setId,
          docTtl=orm.docTtl,
          docTyp=orm.docTyp,
          docCntnt=docCntnt,
          crtUser=self.getUserId(request),
          crtTm=now
        )
        session.add(version)
        stmt = update(DocmtInfo).where(DocmtInfo.docId == docId).values(
          docCntnt=docCntnt,
          updTm=now
        )
        session.execute(stmt)
      return self.success()
    
    # 将文档添加到数据集
    @app.post('/doc/document/to/dataset')
    def documentAddToDataset(form: DocmtToDatasetForm, request: Request):
      require_document_access(form.docId, request)
      self.docsetService.add_to_dataset(reposId=form.reposId, docId=form.docId, userId=self.getUserId(request))
      return self.success()
    
    @app.get('/doc/document/reposid/list/{docId}')
    def documentDatasetList(docId: str, request: Request):
      require_document_access(docId, request)
      with session_scope(True) as session:
        orms = session.query(Dataset).where(Dataset.docId == docId).all()
        idsset = set()
        for orm in orms:
          idsset.add(orm.reposId)
        return self.success(list(idsset))
