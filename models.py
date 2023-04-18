from app import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    slack_user_id = db.Column(db.String(50), nullable=False)
    slack_user_name = db.Column(db.String(100), nullable=False)
    # user_vector = db.Column(db.LargeBinary, nullable=False)

    def __init__(self, slack_user_id, slack_user_name, user_vector):
      self.slack_user_id = slack_user_id
      self.slack_user_name = slack_user_name
      # self.user_vector = user_vector

    @property
    def serialize(self):
      return {
        'id': self.id,
        'slack_user_id': self.slack_user_id,
        'slack_user_name': self.slack_user_name,
      }
    
    
class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    article_external_id = db.Column(db.String(50), nullable=False)
    query = db.Column(db.String(100), nullable=False)
    document = db.Column(db.String(1000), nullable=False)


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
    user_clicked = db.Column(db.Boolean, nullable=False)
    query = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    slack_user_id = db.Column(db.String(50), nullable=False)
    slack_user_name = db.Column(db.String(100), nullable=False)
    article_external_id = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))


    def __init__(self, user_clicked, query, category, slack_user_id, slack_user_name, article_external_id, user_id, article_id):
      self.user_clicked = user_clicked
      self.query = query
      self.category = category
      self.slack_user_id = slack_user_id
      self.slack_user_name = slack_user_name
      self.article_external_id = article_external_id
      self.user_id = user_id
      self.article_id = article_id
       

    @property
    def serialize(self):
      return {
        'id': self.id,
        'user_clicked': self.user_clicked,
        'query': self.query,
        'category': self.category,
        'slack_user_id': self.article_user_id,
        'slack_user_name': self.slack_user_name,
        'article_external_id': self.article_external_id,
        'user_id': self.user_id,
        'article_id': self.article_id
      }