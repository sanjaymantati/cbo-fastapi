import json
import os
from datetime import datetime, timedelta
import time

import pandas as pd

from client.kite_client import KiteClient
from client.smtp_client import GmailSMTPClient
from service.feature_engineering_service import calculate_atr
from service.inference_service import InferenceService
from utility import get_json_from_file
from utility.threading_utils import ThreadingUtils


class CBODetectionService:
    def __init__(self):
        self.kite_client: KiteClient = KiteClient()
        self.historical_data_interval = os.environ.get("HISTORICAL_DATA_INTERVAL")
        self.personal_email = os.environ.get("PERSONAL_EMAIL")

        system_prompts = "./static/prompts/system-prompt.md"
        user_prompts = "./static/prompts/user-prompt.md"
        self.security_file_path = "./static/securities.json"
        self.all_security_file_path = "./static/nse_eq.json"
        self.inference_service: InferenceService = InferenceService(system_prompts,
                                                   user_prompts)
        self.smtp_client: GmailSMTPClient = GmailSMTPClient()

    def get_start_end_date_for_historical_data(self):
        # Current date with time set to 23:00:00
        end_date = datetime.now().replace(hour=23, minute=0, second=0,
                                          microsecond=0)

        # Start date 3 days before with time set to 23:00:00
        start_date = (end_date - timedelta(days=3)).replace(hour=0,
                                                            minute=0,
                                                            second=0,
                                                            microsecond=0)

        # Format both dates as strings
        start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
        end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")

        return start_date_str, end_date_str

    def get_securities(self):
        selected_securities = os.environ.get("SECURITIES_TO_WATCH", "")

        if selected_securities and selected_securities!="":
            all_securities = get_json_from_file(self.all_security_file_path)
            exclude_set = {x.strip() for x in selected_securities.split(",") if
                           x.strip()}  # clean & fast set
            return [obj for obj in all_securities if obj["tradingsymbol"] in exclude_set]
        else:
            return get_json_from_file(self.security_file_path)
    def do_inference(self):
        """Load securities"""
        print(
            f"Scheduled job executed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        securities: list = self.get_securities()
        result_list = ThreadingUtils.process_with_threading(self.inference_single_security, securities)
        """Send the report in mail"""
        table_content = self.prepare_email_table(result_list)
        with open("output.json", "w") as f:
            json.dump(result_list, f, indent=4)
        self.send_email(table_content)

    def inference_single_security(self, security):
        try:
            """For each security fetch data from Kite"""
            start_date, end_date = self.get_start_end_date_for_historical_data()
            historical_data: list = self.kite_client.historical_data(
                security.get("instrument_token"),
                start_date,
                end_date,
                interval=self.historical_data_interval)

            """Convert it to df"""
            df: pd.DataFrame = pd.DataFrame(historical_data)
            df['date'] = pd.to_datetime(df['date'])
            df['atr'] = calculate_atr(df)

            """Build inference data"""
            now = pd.Timestamp.now(tz='Asia/Kolkata')
            today_start = now.normalize()
            tomorrow_start = today_start - pd.Timedelta(days=2)
            filtered_df = df[df['date'] >= today_start]
            # filtered_df = filtered_df.head(40)
            csv_string = filtered_df.to_markdown(index=False)

            """Do inference"""
            metadata = {
                "instrument": security.get("tradingsymbol")
            }
            return self.inference_service.do_inference(csv_string, metadata)
        except Exception as e:
            print("Failed to inference: {}".format(str(e)))
            return None
    def send_email(self, table_content):
        current_time = datetime.now().strftime("%d-%m-%Y %H:%M")
        subject = f"CBO - {current_time}"

        self.smtp_client.send_email(self.personal_email, subject, table_content)

    def prepare_email_table(self, result_list):

        html = """
        <table border="1" cellspacing="0" cellpadding="5" style="border-collapse: collapse; font-family: Arial; font-size: 14px;">
            <thead style="background-color: #f2f2f2;">
                <tr>
                    <th>Name</th>
                    <th>Contraction(%)</th>
                    <th>Start</th>
                    <th>End</th>
                    <th>Breakout(%)</th>
                    <th>Breakout Time</th>
                    <th>Inference</th>
                </tr>
            </thead>
            <tbody>
        """

        for entry in result_list:
            if not entry:
                continue
            instrument = entry.get("instrument") or "-"
            contraction = entry["json_response"]["contraction"]
            breakout = entry["json_response"]["breakout"]

            contraction_strength = contraction["strength"] if contraction[
                "is_present"] else "-"
            contraction_start = contraction["period"]["start_time"] if \
            contraction["is_present"] else "-"
            contraction_end = contraction["period"]["end_time"] if contraction[
                "is_present"] else "-"

            breakout_strength = breakout["strength"] if breakout[
                "is_started"] else "-"
            breakout_time = breakout["start_time"] if breakout[
                "is_started"] else "-"
            inference_time: float = entry["inference_time"] if entry["inference_time"] else "-"

            html += f"""
                <tr>
                    <td>{instrument}</td>
                    <td>{contraction_strength}</td>
                    <td>{contraction_start}</td>
                    <td>{contraction_end}</td>
                    <td>{breakout_strength}</td>
                    <td>{breakout_time}</td>
                    <td>{inference_time:.2f}</td>
                </tr>
            """

        html += """
            </tbody>
        </table>
        """
        return html
