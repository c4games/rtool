
import os

def get_depth_for_path(path):
    path = os.path.normpath(path)
    if path[-1] == os.path.sep:
        path = path[:-1]
    depth = path.count(os.path.sep)
    return depth

if __name__ == '__main__':
    print get_depth_for_path('/')
    print get_depth_for_path('//')
    print get_depth_for_path('/abc')
    print get_depth_for_path('/abc//def')
