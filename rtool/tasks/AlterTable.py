import pymysql
import logging

logger = logging.getLogger("ALTERTABLE")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)



DB_CONFIG = {
	"host":"172.16.153.44",
	"port":51000,
	"user":"root",
	"password":"123456",
	"db":"asset_vega"
	}

TABLE_NAMES = ["assets_android_vega_android_release","assets_ios_vega_ios_release"]

def get_db_con(config):
	try:
		conn = pymysql.connect(host=config.get("host"),user=config.get("user"),passwd=config.get("password"),db=config.get("db"),port=config.get("port"),charset="utf8")
		return conn
	except Exception as e:
		logger.error(e.args)




def alter_table(table_name):
	db_conn = get_db_con(DB_CONFIG)
	try:
		alter_table_sql = ("ALTER TABLE {} "
							"ADD `task_id` int(11) DEFAULT 0, "
							"DROP PRIMARY KEY, "
							"ADD PRIMARY KEY (`asset_tag`,`md5`,`url`,`task_id`)").format(table_name)
		try:
			cur = db_conn.cursor()
			cur.execute(alter_table_sql)
			db_conn.commit()
		except Exception as e:
			logger.error(e.args)
	except Exception as e:
		logger.error(e.args)
	db_conn.close()




if __name__ == '__main__':
	logger.debug("Start Altering Tables")
	for table_name in TABLE_NAMES:
		logger.debug("Start altering {}".format(table_name))
		alter_table(table_name)
		logger.debug("{} altered".format(table_name))
	logger.debug("FIN")



