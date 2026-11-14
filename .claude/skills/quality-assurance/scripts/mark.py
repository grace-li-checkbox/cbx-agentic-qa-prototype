import json
import os
import sys
import time


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: mark.py <case dir> <start | step name | end>")
    case_dir, name = sys.argv[1], sys.argv[2]
    os.makedirs(case_dir, exist_ok=True)
    start_file = os.path.join(case_dir, "video-start")
    if name == "start":
        with open(start_file, "w") as handle:
            handle.write(str(time.time()))
        print("start")
        return
    with open(start_file) as handle:
        start = float(handle.read())
    marks_file = os.path.join(case_dir, "marks.json")
    marks = {}
    if os.path.exists(marks_file):
        with open(marks_file) as handle:
            marks = json.load(handle)
    marks[name] = round(time.time() - start, 1)
    with open(marks_file, "w") as handle:
        json.dump(marks, handle)
    print(name, marks[name])


if __name__ == "__main__":
    main()
