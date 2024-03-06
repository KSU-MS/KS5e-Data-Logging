from parser_utils.folder_selection_utils import select_folder_and_get_path,select_folder_and_get_path_dbc,open_path
from parser_utils.download_latest_dbc_from_releases import download_latest_release
from parser_utils.logplotter import cantools_plot_csv
from parser_api import *
from parser_utils.big_text_prints import *
import sys
import argparse
import subprocess
import importlib
import parser_utils.parser_logger as parser_logger, logging
sys.path.insert(1, "../telemetry_parsers")
########################################################################
# Entry Point to Framework
########################################################################

def main(args):
    logging.info("Welcome to KSU motorsports CAN parser")
    logging.info(PARSER_INIT_TEXT)
    logging.info("The process will be of two parts: CSV to CSV parsing, and then CSV to MAT parsing.")
    dbc_found = False
    dbc_files_folder_good = True
    parser_exe_path = os.getcwd()
    logging.info(parser_exe_path)
    if args.getdbc:
        logging.info("Downloading latest dbc")
        download_latest_release()
        
    logging.info("Looking for 'dbc-files' folder: ")
    while not dbc_found:
        if not os.path.exists("dbc-files") or dbc_files_folder_good == False:
            logging.warning("'dbc-files' folder was not found or failed to load dbcs.")
            logging.info("please select the folder with dbc files to use for parsing...")
            while True:
                try:
                    dbc_files_path = select_folder_and_get_path_dbc()
                except:
                    logging.error("could not open tkinter prompt to select folder")
                    logging.error("please get your dbc files in 'dbc-files' then try to run the program again")
                    break
                for file_name in os.listdir(dbc_files_path):
                    if file_name.endswith(".dbc"):
                        logging.info(f"Found DBC file: {file_name}")
                        dbc_found = True
                if dbc_files_path is not None:
                    dbc_file = get_dbc_files(dbc_files_path)
                elif dbc_files_path is None:
                    logging.warning(f"selected path was {dbc_files_path}, which means you exited or cancelled the prompt")
                    logging.warning(f"exiting the program in {PARSER_EXIT_TIMEOUT} secs ! byebye")
                    time.sleep(PARSER_EXIT_TIMEOUT)
                    sys.exit()
                if dbc_found and dbc_file is not None:
                    break
                else:
                    logging.warning(f"No DBCs found in {dbc_files_path}")
                    logging.warning("Please select another folder...")

        elif os.path.exists("dbc-files") and dbc_files_folder_good:
            logging.info("dbc-files folder found")
            dbc_files_path = ('dbc-files')

            dbc_file = get_dbc_files(dbc_files_path)
            if dbc_file is not None:
                break
            elif dbc_file is None:
                dbc_files_folder_good = False

    logging.info("beginning CSV to CSV parsing")
    logging.info(PARSER_STARTING_TEXT)
    parsing_folder_path=None
    if  not args.test:
        logging.info("Select a folder which contains the raw logs to be parsed")
        try:
            parsing_folder_path = select_folder_and_get_path()
        except:
            logging.error("could not open tkinter prompt to select folder")
    elif args.test:
        # 'test' folder includes a csv with a bit of meaningful data in it so we can test parsing against it
        # TODO: long term, host a batch of example csvs, and download them rather than storing here
        logging.info(f"Setting path to test due to 'test' arg being true: {args.test}")
        parsing_folder_path='./test'
    try:
        parsed_folder_stats = parse_folder(parsing_folder_path, dbc_file=dbc_file,get_summary=args.summary)
        logging.debug(json.dumps(parsed_folder_stats,indent=3))
        if args.summary:
            with open(str(parsing_folder_path)+"/parsing_info.json", 'w') as f:
                json.dump(parsed_folder_stats, f,indent=4)
                logging.info("saved parsing summary json")
        logging.info("Finished CSV to CSV parsing.")
    except (TypeError,FileNotFoundError) as e:
        logging.error(f"Error ({type(e)}-{e}) when trying to parse folder {parsing_folder_path} :(")
        logging.warning("Parsing folder step failed")
        
    logging.info(PARSER_CSV_FINISHED_TEXT)
    logging.info("Beginning CSV to MAT parsing...")
    
    logging.info(PARSER_MAT_START_TEXT)
    if not args.skipmat:
        create_mat_success = create_mat('temp-parsed-data',parser_exe_path,parsed_folder_stats["logs"][0]["debug_info"]["start_timestamp"])
    
    if create_mat_success:
        logging.info("Finished CSV to MAT parsing.")
    elif not create_mat_success:
        logging.warning("CSV to MAT parsing step failed")
        
    logging.info(PARSER_MAT_FINISHED_TEXT)
    logging.info("Parsing Complete.")
    logging.info(PARSER_FINISHED_TEXT)
    
    if parsing_folder_path is not None:
        logging.info(f"the parsed data is in {parsing_folder_path}")
        logging.info(f"opening the folder with your parsed files: '{parsing_folder_path}'")
        try:
            open_path(parsing_folder_path)
        except:
            logging.error(f"opening {parsing_folder_path} failed.")
    logging.info(f'Program exiting in {PARSER_EXIT_TIMEOUT} seconds...')
    time.sleep(PARSER_EXIT_TIMEOUT)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='KSU Motorsports parser! \nThese args configure how the parser is run')
    parser.add_argument('--getdbc',action="store_true" , help='include this flag if you want to download the latest dbc.')
    parser.add_argument('-p','--plot',action="store_true" , help='include this flag if you want to plot the logs.')
    parser.add_argument('-s','--summary',action="store_true" , help='include this flag if you want to save summary info of the logs.')
    parser.add_argument('--test',action="store_true",help='including this flag will make the parser target the "test" directory for folders')
    parser.add_argument('--gui',action="store_true",help="this flag will make the parser run in gui mode (NOT YET IMPLEMENTED)")
    parser.add_argument('-v','--verbose',action="store_true",help="will show debug prints (this will spam your console but show more info)")
    parser.add_argument("--skipmat",action="store_true",help="this flag will make the parser skip matlab file creation")
    args = parser.parse_args()
    parser_logger.setup_logger(args.verbose)
    
    if '_PYIBoot_SPLASH' in os.environ and importlib.util.find_spec("pyi_splash"):
        import pyi_splash
        pyi_splash.update_text("UPDATED TEXT")
        time.sleep(5)
        pyi_splash.close()
        logging.debug('App loaded and splash screen closed.')
    main(args)
