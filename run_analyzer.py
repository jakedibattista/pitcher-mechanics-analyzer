from pitcher_analyzer import PitcherAnalyzer
import argparse

def main():
    parser = argparse.ArgumentParser(description='Baseball Pitcher Analysis Tool')
    parser.add_argument('--video', required=True, help='Path to the pitch video file')
    parser.add_argument('--data', required=True, help='Path to historical data CSV')
    
    args = parser.parse_args()
    
    analyzer = PitcherAnalyzer()
    result = analyzer.should_pull_pitcher(
        video_path=args.video,
        database_path=args.data
    )
    print(f"\nAnalysis Result:\n{result}")

if __name__ == "__main__":
    main() 