from pathlib import Path

import pitlib.db as db
import pitlib.tree as tree

import argh

def init():
    repo_path = db.db_path(expect_exists=False)
    if repo_path.is_dir():
        print("Already a pit directory: {}".format(repo_path))
        exit(0)

    repo_path.mkdir()
    repo_path.joinpath("objects").mkdir()
    print("Created new pit repository: {}".format(repo_path))

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
    
