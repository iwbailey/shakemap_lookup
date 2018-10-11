
import yaml

with open("search_params.yaml", 'r') as stream:
    try:
        this = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)

# print(this)

searchParams = this

print(searchParams)
