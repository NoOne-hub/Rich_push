from sqlalchemy import Column, Integer, String,DECIMAL

from app import db


class Trichpush(db.Model):
    __tablename__ = 't_rich_push'

    id = Column(Integer, primary_key=True)
    rich_id = Column(String(150), nullable=False, info="基金号")
    rich_name = Column(String(60), info="备注")
    rich_scope = Column(String(10), info="涨跌幅度", default="-0.01")
    rich_code = Column(String(100), info="server酱推送key")
    rich_time = Column(String(100), info="推送时间", default="14:50")
    rich_status = Column(String(10), info="状态", default="停止")

    def to_json(self):
        if hasattr(self, '__table__'):
            return {i.name: getattr(self, i.name) for i in self.__table__.columns}
        raise AssertionError('<%r> does not have attribute for __table__' % self)

class rich_all(db.Model):
    __tablename__ = 't_all'
    id = Column(Integer, primary_key=True)
    rich_id = Column(String(30), nullable=False, info="基金号")
    rich_name = Column(String(60), info="基金名称")
