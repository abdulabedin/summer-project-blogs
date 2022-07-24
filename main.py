import requests
import json

TEMPLATE_URL = "https://raw.githubusercontent.com/OpenLiberty/blogs/prod/templates/beta-release-post.adoc"

def get_titles(issues, is_beta):
    titles = []
    prefix = "BETA BLOG - " if is_beta else "GA BLOG - "
    for issue in issues:
        titles.append(issue["title"].replace(prefix, ""))
    return titles

def make_feature_list(titles):
    titles = []

    for i, title in enumerate(titles):
        titles.append(f'* <<SUB_TAG_{i}, {title}>>') # TODO: get/make meaningful tags

    return '\n'.join(titles)

def make_feature_content(titles): # TODO
    length = len(titles)
    content = []
    for i in range(length):
        content.append(f"[#SUB_TAG_{i}]\n=== {titles[i]}")
    return "\n".join(content)

def main():
    version = "22008"
    is_beta = version.endswith("beta")
    ISSUE_URL = f"https://api.github.com/repos/OpenLiberty/open-liberty/issues?labels=blog,target:{version}"

    issues = json.loads(requests.get(ISSUE_URL).text)
    titles = get_titles(issues, is_beta)
    # TODO: extract contents

    # TODO: best practice to locate placeholders
    FEATURE_LIST_SECTION = '''* <<SUB_TAG_1, SUB_FEATURE_TITLE>>
* <<SUB_TAG_2, SUB_FEATURE_TITLE>>
* <<SUB_TAG_3, SUB_FEATURE_TITLE>>'''

    FEATURE_CONTENT_SECTION = '''[#SUB_TAG_1]
=== SUB_FEATURE_TITLE

// // // // // // // //
// FURTHER EXPLANATION OF THIS FEATURE/FUNCTION
// // // // // // // //



[source, java]
----
// // // // // // // //
// EXAMPLE CODE
// // // // // // // //
----'''

    template = requests.get(TEMPLATE_URL).text;
    template = template.replace(FEATURE_LIST_SECTION, make_feature_list(titles))
    template = template.replace(FEATURE_CONTENT_SECTION, make_feature_content(titles))
    # TODO: replace RELEASE_VERSION

    with open("output.adoc", "w") as fp:
        fp.write(template)

if __name__ == "__main__":
    main()