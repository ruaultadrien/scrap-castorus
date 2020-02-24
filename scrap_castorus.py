
import os


from utils import build_df_from_centers
from constants import OUTPUT_DIR


def main():
    centers = [('Angers', 19447), ('Nantes', 17969),
               ('Le+Mans', 31646), ('Tours', 15280)]
    df = build_df_from_centers(centers, radius=30)

    if not os.path.isdir(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    output_path = os.path.join(OUTPUT_DIR, 'all_data.csv')
    df.to_csv(output_path)


if __name__ == '__main__':
    main()
