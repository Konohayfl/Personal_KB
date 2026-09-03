from fastapi import FastAPI
from sqlalchemy import text

from server.api.BaseApi import BaseApi
from server.db.DbManager import ENGINE


class HealthApi(BaseApi):
  def __init__(self, app: FastAPI):
    BaseApi.__init__(self)

    @app.get('/health')
    def health():
      try:
        with ENGINE.connect() as connection:
          connection.execute(text('SELECT 1'))
      except Exception:
        return self.fail(code='9999', msg='数据库连接不可用')
      return self.success({
        'status': 'ok',
        'database': 'ok'
      })
