import logging
import traceback

def safe_process(game, func):
    try:
        return func(game)
    except Exception as e:
        logging.error(f"Error processing game: {e}", exc_info=True)
        traceback.print_exc()
        return []