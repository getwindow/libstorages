#! -*- encoding:utf-8 -*-

import os
import xml.sax

from pdb import set_trace as bp
import cloudstore
import cloudstore.backends

class SaxParserFactory:
	def create ( self ):
		return xml.sax.make_parser ( )


class AdapterFactory:
    def __init__ ( self ):
        pass

    def create ( self, vender_id, config ):
        adapter_module_name = "cloudstore.backends.%s" % vender_id.lower ( )
        backends = __import__ ( adapter_module_name )
        adapter_module = getattr ( cloudstore.backends, vender_id.lower ( ) )
        return getattr ( adapter_module , "Adapter" ) ( config ) 


class StoreFactory:
    """
    格式 (VENDER_ID)_ACCESS_KEY (VENDER_ID)_SECRET_KEY 厂商id的大写。
    两个环境变量获得初始默认的配置
    """

    def __init__ ( self ):
        self.adapter_factory = AdapterFactory ( )

    def create ( self, vender_id ):
        if not vender_id in cloudstore.config.VENDER:
            raise StandardError ( "Not implement this vender." )

        ACCESS_KEY = os.getenv ( "%s_ACCESS_KEY" % vender_id.upper ( ) )
        SECRET_KEY = os.getenv ( "%s_SECRET_KEY" % vender_id.upper ( ) )
        config_class_name  = "%sConfig" % vender_id.upper ( )
        has_specify_config = hasattr ( cloudstore.config, config_class_name )

        if not has_specify_config:
            config = Config ( access_key = ACCESS_KEY, secret_key = SECRET_KEY )
        else:
            config = getattr ( cloudstore.config, config_class_name ) ( access_key = ACCESS_KEY, secret_key = SECRET_KEY )

        config.adapter = self.adapter_factory.create ( vender_id, config )
        return cloudstore.Store ( config )