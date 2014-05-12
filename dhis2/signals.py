import logging
from utils.operations import commit_signal
from stock.apps import *

logger = logging.getLogger("rapidsms")

def stock_level_dhis2_commit(message, stock_levels={}, **kwargs):
    """
    A stock level commit stub
    """
    logger.debug("Fake stock level commit to DHIS2: %s" % repr(stock_levels))
    message.respond("Stock level commit made")

def stock_out_dhis2_commit(message, stock_code=None, **kwargs):
    """
    A stock level commit stub
    """
    logger.debug("Fake stock out commit to DHIS2: %s" % repr(stock_code))
    message.respond("Stock out commit made")


#commit_signal.connect(stock_level_dhis2_commit, sender=StockLevel)
#commit_signal.connect(stock_out_dhis2_commit, sender=StockOut)