# Local development guide

Install `vespa-cli` using `brew install vespa-cli`

Ensure you have pyvespa installed (`pip3 install pyvespa`)

Run the following

```sh
vespa config set target cloud
vespa config set application secondbrain.secondbrain
vespa auth cert -N
```

To generate the Vespa config files (in `vespa/`) run `python3 vespa_config.py`.
This should enable easy enough iteration with the Vespa cloud instance

# Running RAG

The LLM is run on Modal - a serverless GPU cloud platform. You'll need an API
key for this. Contact Rohan for this key.



