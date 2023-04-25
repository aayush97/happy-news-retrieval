from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    slack_user_id = db.Column(db.String(50), nullable=False)
    slack_user_name = db.Column(db.String(100), nullable=False)
    user_vector = db.Column(db.LargeBinary, nullable=False)

    def __init__(self, slack_user_id, slack_user_name, user_vector):
      self.slack_user_id = slack_user_id
      self.slack_user_name = slack_user_name
      self.user_vector = user_vector

    @property
    def serialize(self):
      return {
        'id': self.id,
        'slack_user_id': self.slack_user_id,
        'slack_user_name': self.slack_user_name,
        'user_vector': self.user_vector
      }
    
    
class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    article_external_id = db.Column(db.String(50), nullable=False)
    query = db.Column(db.String(100), nullable=False)
    document = db.Column(db.String(1000), nullable=False)
    #article_vector = db.Column(db.LargeBinary, nullable=False)


    def __init__(self, article_external_id, query, document):
        self.article_external_id = article_external_id
        self.query = query
        self.document = document
    
    @property
    def serialize(self):
      return {
          'id': self.id,
          'article_external_id': self.article_external_id,
          'query': self.query,
          'document': self.document
      }
    
class Tweet(db.Model):
    __tablename__ = 'tweets'

    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(100), nullable=False)
    documents = db.Column(db.String(1000))
    

    def __init__(self, query, documents):
        self.query = query
        self.documents = documents
    
    @property
    def serialize(self):
      return {
        'id': self.id,
        'query': self.query,
        'documents': self.documents
      }

class UserInteraction(db.Model):
    __tablename__ = 'user_interactions'

    id = db.Column(db.Integer, primary_key=True)
    user_clicked = db.Column(db.Boolean, nullable=True)
    query = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    slack_user_id = db.Column(db.String(50), nullable=True)
    slack_user_name = db.Column(db.String(100), nullable=True)
    article_external_id = db.Column(db.String(50), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))


    def __init__(self, slack_user_id, slack_user_name, article_id):
      self.slack_user_id = slack_user_id
      self.slack_user_name = slack_user_name
      self.article_id = article_id
       

    @property
    def serialize(self):
      return {
        'slack_user_id': self.slack_user_id,
        'slack_user_name': self.slack_user_name,
        'article_id': self.article_id
      }