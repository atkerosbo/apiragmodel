from database import Base
from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.sql.sqltypes import TIMESTAMP

class Data(Base):
    __tablename__ = "data"
    id = Column(Integer, primary_key=True, nullable=False)
    page_number = Column(Integer, nullable = False)
    page_char_count = Column(Integer, nullable = False)
    page_word_count =Column(Integer, nullable = False)
    page_sentence_count = Column(Integer, nullable = False)
    page_token_count = Column(Integer, nullable = False)
    text = Column(String, nullable=False)
    embedding = Column(LargeBinary, nullable=False)

