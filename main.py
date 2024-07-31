from src import bjson, conversions, JOAAThash, updateDatabase
import os, sys, shutil, random, string, json

character = string.ascii_letters + string.digits
random_string = ''.join(random.choice(character) for _ in range(16))

directory = os.path.dirname(__file__)
main_string = bjson.convertBjsonToJson(sys.argv[1]) # Aanroep van functie krijgt alle tekst voor binair json-bestand. Alleen testen.

if '"size": [' not in main_string:
    raise ValueError
else:
    # Schrijf geconverteerde string naar JSON-bestand
    json_path = os.path.join(directory, f"{random_string}.json")
    with open(json_path, 'w') as json_file:
        json_file.write(main_string)

    # Lees de JSON-gegevens uit het gegenereerde bestand
    with open(json_path, "r") as new_json_file:
        json_data = json.load(new_json_file)

    # Verwerk de JSON-bestandsgegevens en haal eruit wat nodig is.
    for key, value in json_data.items():
        if key.startswith("geometry.") and "bones" in value:
            bones = value["bones"]
            output_lines = []
            for bone in bones:
                if "name" in bone and "cubes" in bone:
                    name = bone["name"]
                    cubes = bone["cubes"]
                    for cube in cubes:
                        if "origin" in cube and "size" in cube:
                            origin = cube["origin"]
                            size = cube["size"]
                            output_lines.append(f"{name}")
                            output_lines.append(f"{origin[0]}, {origin[1]}, {origin[2]}")
                            output_lines.append(f"{size[0]}, {size[1]}, {size[2]}")
                            output_lines.append("")  # Blank line for separation

            # Write the output to the appropriate text file
            output_directory = os.path.join(directory, "output")
            os.makedirs(output_directory, exist_ok=True)
            output_path = os.path.join(output_directory, f"{key}.txt")
            with open(output_path, 'w') as output_file:
                output_file.write("\n".join(output_lines))

    print(f"Output files have been saved in {output_directory}")


def read_output_files():
    output_directory = input(r"Plak hier de locatie van uw model: ")
    model_data = {}
    with open(os.path.join(output_directory), 'r') as file:
        lines = file.readlines()
        model_name = output_directory.replace('.txt', '')
        model_data[model_name] = []
        for i in range(0, len(lines), 4):
            name = lines[i].strip()
            origin = list(map(float, lines[i+1].strip().split(', ')))
            size = list(map(float, lines[i+2].strip().split(', ')))
            model_data[model_name].append((name, origin, size))
    return model_data

def generate_obj(model_data, output_directory):
    obj_lines = []
    vertex_count = 1

    for model_name, cubes in model_data.items():
        obj_lines.append(f"o {model_name}")
        for name, origin, size in cubes:
            x, y, z = origin
            dx, dy, dz = size

            # Berekent het objectbestand
            vertices = [
                (x,     y,     z    ),
                (x+dx,  y,     z    ),
                (x+dx,  y+dy,  z    ),
                (x,     y+dy,  z    ),
                (x,     y,     z+dz ),
                (x+dx,  y,     z+dz ),
                (x+dx,  y+dy,  z+dz ),
                (x,     y+dy,  z+dz )
            ]
            for vx, vy, vz in vertices:
                obj_lines.append(f"v {vx} {vy} {vz}")

            # Definieert de faces/vertex-dingen
            faces = [
                (1, 2, 3, 4),
                (5, 8, 7, 6),
                (1, 5, 6, 2),
                (2, 6, 7, 3),
                (3, 7, 8, 4),
                (5, 1, 4, 8)
            ]
            for f1, f2, f3, f4 in faces:
                obj_lines.append(f"f {vertex_count+f1-1} {vertex_count+f2-1} {vertex_count+f3-1} {vertex_count+f4-1}")

            vertex_count += 8

    # schrijft de gegevens naar een objectbestand in de uitvoermap.
    obj_path = os.path.join(output_directory, f"{model_name}.obj")
    with open(obj_path, 'w') as obj_file:
        obj_file.write("\n".join(obj_lines))

    print(f".obj file has been saved to {obj_path}")

directory = os.path.dirname(__file__)
output_directory = os.path.join(directory, "output")

model_data = read_output_files()
generate_obj(model_data, output_directory)