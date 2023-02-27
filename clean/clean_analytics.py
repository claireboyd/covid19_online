import pandas as pd
import itertools
from collect.analytics_data import get_analytics_by_agency, get_analytics_by_report
from collect.utils import REPORT_NAME, AGENCY_NAME
from .datatype import DataType
from collections import defaultdict

# Regex to clean URLS
# Add merge column with strings of dates and merge


class AnalyticsData(DataType):
    def __init__(self, report_type, years):
        self.report_type = report_type
        self.years = years
        self.data = defaultdict(None)

    def sum_by(self, col, in_place=True):
        """
        Cleans dataframe and sums values
        """
        to_sum = defaultdict(None)
        for name, report in self.data.items():
            to_sum[f"{name}_sum"] = report.groupby(col, as_index=False).sum()

        if in_place:
            self.data = to_sum
        else:
            self.modified_data = to_sum

    def split_by_year(self, in_place=True):
        """
        Splits aggegrated yearly data into multiple dataframes per year.
        """
        by_year = defaultdict(None)
        for pair in itertools.product(self.report_type, self.years):
            report, year = pair
            # Convert date to datetime
            self.data[report].date = pd.to_datetime(self.data[report].date)
            year_df = self.data[report][self.data[report].date.dt.year == year]
            # Convert date back to string to merge datasets
            year_df.date = year_df.date.map(str)
            by_year[f"{year}_{report}"] = year_df

        if in_place:
            self.data = by_year
        else:
            self.modified_data = by_year

    def export(self, modified=False):
        """
        Exports data to CSV files in the data folder.
        """
        export_data = self.data
        if modified:
            export_data = self.modified_data

        for (
            name,
            df,
        ) in export_data.items():
            df.to_csv(f"data/{name}.csv", index=False)


class AgencyData(AnalyticsData):
    def __init__(self, agency, years, report_type):
        super().__init__(report_type, years)
        self.agency = agency

    def fetch_data(self):
        """
        Fetches and structures API data based on years and number of reports

        Returns named tuple holding pandas df for each report type.
        """
        for report in self.report_type:
            print(f"Collecting data on {report}.")

            self.data[report] = get_analytics_by_agency(
                self.agency, (self.years[0], self.years[-1]), report
            )


class ReportData(AnalyticsData):
    def __init__(self, report_type, years):
        super().__init__(report_type, years)

    def fetch_data(self):
        """
        Fetches data for specified reports.
        """
        for report in self.report_type:
            print(f"Collecting data on {report}.")
            self.data[report] = get_analytics_by_report(
                report, (self.years[0], self.years[-1])
            )
