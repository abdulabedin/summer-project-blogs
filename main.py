import sys
import requests
import json
import re

TEMPLATE_URL = "https://raw.githubusercontent.com/OpenLiberty/blogs/prod/templates/beta-release-post.adoc"

def get_linked_issue(body):
    result = re.search(r'See (?:the )?Beta blog issue.+?(\d+)', body, re.IGNORECASE)
    if result:
        print('result', result.group(1))
        return json.loads(requests.get(f'https://api.github.com/repos/OpenLiberty/open-liberty/issues/{result.group(1)}').text)['body']
    return None

def make_blog(issues, is_beta): # TODO: inconsistency in blog posts, hard to tackle
    titles = []
    contents = []
    prefix = "BETA BLOG - " if is_beta else "GA BLOG - "

    for i, issue in enumerate(issues):
        title = issue["title"].replace(prefix, "")
        body = get_linked_issue(issue['body']) or issue['body']

        # find the content of blog
        splitted = body.split(r"Where can they find out more about this specific update (eg Open Liberty docs, Javadoc) and/or the wider technology?")
        # currently there's a typo in the template and some people may correct it so we have to try both
        if len(splitted) < 2:
            splitted = body.split(r'Write a paragraph to summarises the update, including the following points:')
        if len(splitted) < 2:
            splitted = body.split(r'Write a paragraph to summarise the update, including the following points:')
        print(splitted[1])
        assert(len(splitted) >= 2)
        body = splitted[1].split("## What happens next?")[0]
        # print(body)

        titles.append(f'* <<SUB_TAG_{i}, {title}>>') # TODO: get/make meaningful tags
        contents.append(f'// {issue["html_url"]}\n[#SUB_TAG_{i}]\n=== {title}\n{body}')

    return '\n'.join(titles), '\n'.join(contents)

def main():
    arg_count = len(sys.argv) - 1
    if arg_count != 4:
        print("Expecting 4 arguments (version number, data of publish, author name, GitHub username), check the GitHub action.", file=sys.stderr)
        exit(1);

    version = sys.argv[1]
    version_no_dots = version.replace('.', '');
    is_beta = version_no_dots.endswith("beta")
    publish_date = sys.argv[2]
    author_name = sys.argv[3]
    github_username = sys.argv[4]

    ISSUE_URL = f"https://api.github.com/repos/OpenLiberty/open-liberty/issues?labels=blog,target:{version_no_dots}"

    issues = json.loads(requests.get(ISSUE_URL).text)
    # print(issues)
    toc, content = make_blog(issues, is_beta)

    # TODO: best practice to locate placeholders
    TOC_SECTION = '''* <<SUB_TAG_1, SUB_FEATURE_TITLE>>
* <<SUB_TAG_2, SUB_FEATURE_TITLE>>
* <<SUB_TAG_3, SUB_FEATURE_TITLE>>'''

    CONTENT_SECTION = '''[#SUB_TAG_1]
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
    # maybe chain those replace calls?
    template = template.replace(TOC_SECTION, toc) \
                       .replace(CONTENT_SECTION, content) \
                       .replace("RELEASE_VERSION", version) \
                       .replace('AUTHOR_NAME', author_name) \
                       .replace('GITHUB_USERNAME', github_username)

    filename = f"{publish_date}-{version}.adoc"
    with open(f"posts/{filename}", "w") as fp:
        fp.write(template)

if __name__ == "__main__":
    main()
