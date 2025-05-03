from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# 创建基类
Base = declarative_base()

# 定义模型
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    
# 创建引擎
engine = create_engine('sqlite:///:memory:')

# 创建表
Base.metadata.create_all(engine)

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# 添加数据
user = User(name='test')
session.add(user)
session.commit()

# 查询数据
users = session.query(User).all()
for user in users:
    print(f"User ID: {user.id}, Name: {user.name}")
