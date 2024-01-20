# Local development guide

Install `vespa-cli` using `brew install vespa-cli`

Ensure you have pyvespa installed (`pip3 install pyvespa`)

Run the following

```sh
vespa config set target cloud
vespa config set application secondbrain.secondbrain
vespa auth cert -N
```

