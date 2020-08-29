from pathlib import Path


def get_requirement_lines():
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

    return req_content, meta_lines[requirements_start:requirements_end]


def test_requirement_versions_equal():
    req_content, meta_content = get_requirement_lines()

    #  filter all whitespace from dependencies list entries and assert that they are equal
    req_dependencies = ["".join(dep.split()) for dep in req_content]
    meta_dependencies = [
        "".join(dep.split()).replace("-", "")
        for dep in meta_content[6:]
        if "python" not in dep
    ]
    assert len(req_dependencies) == len(meta_dependencies)
    assert set(req_dependencies) == set(meta_dependencies)


def test_requirements_setuptools_equal():
    _, meta_content = get_requirement_lines()

    setup_dependencies = [
        "".join(dep.split()).replace("-", "")
        for dep in meta_content
        if "setuptools" in dep
    ]
    assert setup_dependencies[0] == setup_dependencies[1]


def test_version():
    from pandas_visual_analysis.version import __version__

    assert __version__ is not None
    assert isinstance(__version__, str)
