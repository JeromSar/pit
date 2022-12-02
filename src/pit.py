from pathlib import Path

import pitlib.tree as tree

import argh

def init():
    pit_path = Path.cwd().joinpath(".pit")
    if pit_path.is_dir():
        print("Already a pit directory: {}".format(pit_path))
        exit(0)

    pit_path.mkdir()
    pit_path.joinpath("objects").mkdir()
    print("Created new pit repository: {}".format(pit_path))

def status():
    tree_obj = tree.from_dir(Path.cwd())
    print(tree_obj)

def main():
    parser = argh.ArghParser()
    parser.add_commands([
        init,
        status
    ])
    parser.dispatch()



if __name__ == '__main__':
    main()
    
