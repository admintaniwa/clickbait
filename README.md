# Clickbait Detector Dashboard

This project is a dashboard that monitors daily news headlines from major Spanish media outlets and classifies them as either clickbait or non-clickbait. The dashboard provides visualizations of the percentage of clickbait headlines over time and allows users to input their own headlines for classification.

## Project Structure

```
front/
    .devcontainer/
        devcontainer.json
    app/
        assets/
            base-styles.css
            fonts.css
            spc-custom-styles.css
        cb.py
        data/
            agregados_es.csv
            noticias_es_30dias.csv
            noticias_es_proc.csv
            noticias_es.csv
        etl_procon.py
        etl.py
        modelo/
            clickbait_es/
                .gitattributes
                ...
        Procfile
        sql/
            01_create_tables.sql
        utils/
            app.py
            memory.py
            sample.py
    Dockerfile
    env.joselu
    README.md
    requirements.txt
train/
    beto_transformer_train_clickbait.ipynb
```

## Setup

1. **Clone the repository:**
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Set up environment variables:**
    Create a `.env` file in the `front/app` directory with the following variables:
    ```
    NEWS_FILE_PATH=path/to/news_file.csv
    AGG_FILE_PATH=path/to/agg_file.csv
    LAST30_FILE_PATH=path/to/last30_file.csv
    SERPAPI_KEY=your_serpapi_key
    DB_USER=your_db_user
    DB_PASS=your_db_password
    DB_HOST=your_db_host
    DB_PORT=your_db_port
    DB_NAME=your_db_name
    ```

## Running the ETL Process

The ETL process extracts news headlines, transforms them using a clickbait classification model, and loads the data into a database.

```sh
python front/app/etl.py
```

## Running the Dashboard

Start the Dash application to view the dashboard.

```sh
python front/app/cb.py
```

## Usage

- **Dashboard:** Monitor the percentage of clickbait headlines over time and view detailed data for each news source.
- **Headline Classification:** Input a headline to classify it as clickbait or non-clickbait.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Dash](https://dash.plotly.com/)
- [Transformers](https://huggingface.co/transformers/)
- [SerpApi](https://serpapi.com/)

For more details, visit the [project blog](https://taniwa.es/articles/clickbait_es/).
