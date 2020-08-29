from pathlib import Path
import yaml


def test_requirement_versions_equal():

    req_path = Path(__file__).parent / "../requirements.txt"
    with req_path.open() as f:
        req_content = f.readlines()

    meta_path = Path(__file__).parent / "../conda/meta.yaml"
    with meta_path.open() as f:
        meta_lines = f.readlines()

        #  meta.yaml contains python extensions e.g. {% set data = load_setup_py_data() %}
        #  this means we can only read the specific requirements section from requirements_start to requirements_end
        line_number = 0
        for line in meta_lines:
            if "requirements" in line:
                requirements_start = line_number
                break
            line_number = line_number + 1

        for line in meta_lines[requirements_start + 1 :]:
            if line.startswith("  ") or line == "\n":
                line_number = line_number + 1
            else:
                break

        requirements_end = line_number
        meta_str = "".join(meta_lines[requirements_start:requirements_end])
        meta_content = yaml.load(meta_str)

    #  filter all whitespace from dependencies list entries and assert that they are equal
    req_dependencies = ["".join(dep.split()) for dep in req_content]
    meta_dependencies = [
        "".join(dep.split())
        for dep in meta_content["requirements"]["run"]
        if dep != "python"
    ]
    assert len(req_dependencies) == len(meta_dependencies)
    assert set(req_dependencies) == set(meta_dependencies)


def test_version():
    from pandas_visual_analysis.version import __version__

    assert __version__ is not None
    assert isinstance(__version__, str)
