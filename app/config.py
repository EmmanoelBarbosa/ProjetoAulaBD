# Configuração dos BDs

# Conectando ao BD SQL
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root@127.0.0.1:3306/bdpos"

# Conectando ao bd NoSQl Mongodb
MONGO_URL = "mongodb://localhost:27017"
MONGO_DB = "vendas"
MONGO_COLLECTION = "dashboard"