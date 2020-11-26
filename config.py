import os

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://%s:6379" % REDIS_HOST)
DEFAULT_OUTDIR = os.environ.get("DEFAULT_OUTDIR", "./")
SKELETON_DIR = os.environ.get("SKELETON_DIR", "/config/")
ATLAS_API = os.environ.get("ATLAS_API", "https://api-dev.mykro.be")
TB_TREE_PATH_V1 = os.environ.get("TB_TREE_PATH_V1", "data/tb_newick.txt")
BIGSI_URL = os.environ.get("BIGSI_URL", "mykrobe-atlas-bigsi-aggregator-api-service/api/v1")
BIGSI_BUILD_URL = os.environ.get("BIGSI_BUILD_URL", "http://bigsi-api-service-small")
BIGSI_BUILD_CONFIG = os.environ.get("BIGSI_BUILD_CONFIG", "/etc/bigsi/conf/config.yaml")
REFERENCE_FILEPATH = os.environ.get("REFERENCE_FILEPATH", "/config/NC_000962.3.fasta")
GENBANK_FILEPATH = os.environ.get("GENBANK_FILEPATH", "/config/NC_000962.3.gb")

ATLAS_AUTH_SERVER = os.getenv('ATLAS_AUTH_SERVER')
ATLAS_AUTH_CLIENT_ID = os.getenv('ATLAS_AUTH_CLIENT_ID')
ATLAS_AUTH_CLIENT_SECRET = os.getenv('ATLAS_AUTH_CLIENT_SECRET')
ATLAS_AUTH_REALM = os.getenv('ATLAS_AUTH_REALM', 'atlas')

MYKROBE_VERSION = os.getenv('MYKROBE_VERSION')
BWA_VERSION = os.getenv('BWA_VERSION')
SAMTOOLS_VERSION = os.getenv('SAMTOOLS_VERSION')
