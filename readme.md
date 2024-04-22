# Shepherding Program

Program for the paper "Swarm Shepherding Using Bearing-only Measurements".

## Config File

For instance, use this command to set config file `config/demo.json`.

```bash
python3 main.py -p "config/demo.json"
```

## Description of files

- `main.py` and `shepherding/trial.py` are key files.
- `shepherding/model` is the folder of sheep model and shepherd model.
- `shepherding/method` is the folder of shepherding algorithm.
- `shepherding/util/` is used to generate graphs/videos.
- `sys/` is used to run the program parallely.
- `../shepherding-log` is used to store simulation data runned by the program. 
- `graph` is used to regenerate figures based on the simulation data.

##  Program for paper

- `shepherding/method/degree/degree.py` corresponds to the proposed shepherding algorithm.
- `config/1_shepherd-multi` corresponds to the initial configurations.
- `config/2_shepherd-angle` corresponds to the initial configurations in increasing angle errors.
- `config/3_shepherd_no-comm` corresponds to the intial configurations in shepherding with no communication.
- `../shepherding-log` stores the figures used in the paper. Only one sample data is stored due to the extremely large size of the original simulation data.