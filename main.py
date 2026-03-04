import curses
from tui.flow import run_flow

def main():
    try:
        config = curses.wrapper(run_flow)
        if config:
            print("\n✔  Configuration captured successfully.")
            print(f"   Asset             : {config.ticker}")
            print(f"   Window            : {config.start_date}--{config.end_date}")
            print(f"   Data cardinality  : {config.data_cardinality_label}  (yfinance: '{config.data_cardinality}')")
            print(f"   Output            : {config.output_path}\n")
    except KeyboardInterrupt:
        print("\nAborted.")
    except SystemExit:
        print("\nExited.")


if __name__ == "__main__":
    main()
