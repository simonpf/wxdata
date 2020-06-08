import argparse
import calendar
import sys
import os
import tqdm
import wxdata.products
import wxdata.download.domains
from datetime import datetime, timedelta

def main():
    ###########################################################################
    # Command line arguments
    ###########################################################################
    parser = argparse.ArgumentParser(prog="wxdata download tool",
                                    description=
                                    """
                                    Download sattelite data.
                                    """)
    parser.add_argument("--product",
                        nargs=1,
                        metavar=("<product_class>",),
                        help="Product class to download.")
    parser.add_argument("--provider",
                        nargs="*",
                        metavar="<provider>",
                        help="The data provider from which to download the files.")
    parser.add_argument("--years",
                        nargs="+",
                        metavar="<19xx> .. <20xx>",
                        help="The years for which to download data.")
    parser.add_argument("--months",
                        nargs="*",
                        metavar="<N1> ... <N2>",
                        help="The months for which to download data. Defaults to all"
                        "months of the year.")
    parser.add_argument("--dest",
                        nargs=1,
                        metavar=("<output_folder>",),
                        help="The output directory in which to store the data.")

    args = parser.parse_args()

    try:
        product = getattr(wxdata.products, args.product[0])
    except:
        print(f"Error: The requested product '{args.product}' is unknown.\n")
        parser.print_help()
        return 1

    try:
        provider = getattr(wxdata.download.domains, args.provider[0])
    except:
        print(f"Error: The requested provider '{args.provider}' is unknown.\n")
        parser.print_help()
        return 1

    provider = provider(product)

    years = map(int, args.years)
    if not args.months is None:
        months = map(int, args.months)
    else:
        months = list(range(1, 13))

    output_dir = os.path.expandvars(os.path.expanduser(args.dest[0]))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ###########################################################################
    # Download files
    ###########################################################################

    for y in years:
        for m in months:
            for d in range(calendar.monthlen(y, m)):
                print(f"Processing {y}-{m}-{d}")
                dest = os.path.join(output_dir,
                                    "{:04d}".format(y),
                                    "{:02d}".format(m),
                                    "{:02d}".format(d + 1))
                if not os.path.exists(dest):
                    os.makedirs(dest)
                t0 = datetime(y, m, d + 1)
                t1 = t0 + timedelta(days=1)
                try:
                    files = provider.get_files_in_range(t0, t1)
                except:
                    print("No files found.")
                    continue
                for f in tqdm.tqdm(files):
                    provider.download(f, os.path.join(dest, f))


    return 0

if __name__ == '__main__':
    main()
