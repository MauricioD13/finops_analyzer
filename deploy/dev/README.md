# Docs FOCUS Converter

Command example:

    focus-converter convert-auto \
    --data-path /path/to/billing/data \
    --export-path /output/directory \
    --export-format parquet \
    --validate

Command for multi-files -> Dataset

    focus-converter convert \  
    --provider aws \  
    --data-path /path/to/parquet/dataset/ \  
    --data-format parquet \  
    --parquet-data-format dataset \  
    --export-path /output/directory
