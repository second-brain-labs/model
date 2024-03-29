This repository houses requisite data infrastructure components.

# Vespa

Install `vespa-cli` using `brew install vespa-cli`

Ensure you have pyvespa installed (`pip3 install pyvespa`)

Update the declarative config in `vespa_config.py`.

To generate the Vespa config files (in `vespa/`) run `python3 vespa_config.py`.

Run the following on a k8s cluster to expose the Vespa config server (on 19071)

```sh
kubectl port-forward vespa-0 19071 &
curl -s --head http://localhost:19071/state/v1/health 
vespa deploy vespa/
fg; C-c
```

# LLM

This example is adapted from Modal's guide on running Mistral 8x7b on their
platform. 

Set up your modal config (`modal token new`) or use environment variables.

Deploy the application `modal deploy llm.py`




