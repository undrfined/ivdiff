# ivdiff

scripts to get difference between two [Instant View](https://instantview.telegram.org) templates

## Installing

Install [python3](https://www.python.org/downloads/) and [pip](https://pypi.org/project/pip/).
Then run `git clone https://github.com/undrfined/ivdiff; cd ivdiff; pip install -r requirements.txt`.

## Auth

To authenticate run script `auth.py`:

```
py auth.py +38093******6
```
...and you're ready to go.

## ivdiff.py

get diff for one specific page

usage:

```
py ivdiff.py <Template> <Template> <URL> [-c <cookies file>] [-b <browser>]
```

...where `<Template>` is a template number if it was submitted to contest (for example `45`) or filename with the template code(for example `file.xpath`). Also you can use `~` to download current code from My Templates section.

**Please do a backup of your code before using filename or `~` as one of the templates**

`<URL>` is an URL to diff.

`<browser>` is a browser name (according to [docs](https://docs.python.org/3/library/webbrowser.html)) or path to program to open file

## batchdiff.py

get diff for a lot of pages from file

usage:

```
py batchdiff.py <Template> <Template> <List of URLs> [-c <cookies file>] [-p <pool size>]
```

...where `<List of URLs>` is a filename with list of all the urls you want to diff and `<pool size>` is count of threads you want to use (default 5)

## spider.py

collect all the URLs automatically and get diff for all of them

usage:

```
py spider.py <Template> <Template> <domain> [-c <cookies file>] [-p <pool size>] [-b <browser>] [-w <whitelist>] [-r <restrict xpath>]
```

...where `<domain>` is a domain name (for example `5minutes.rtl.lu`)

`<browser>` is a browser name (according to [docs](https://docs.python.org/3/library/webbrowser.html)) or path to program to open file

`<whitelist>` is a list of xpathes that will be checked in the IV.

`<restrict xpath>` you guessed it, restricts xpathes to be checked in the IV

## checked.py

press "Mark as checked" for all the links in the domain.

usage:

```
py checked.py <domain> [-c <cookies file>]
```
**Please do a backup of your code before using this**

## cdo, do and other awesome macros for diff

You can use macros inside of your IV template code to diff more easily. There are three types of macros:

- `##do [(alias OR template number) list separated with space OR nothing]`, means "do this block of code for **d**iff **o**nly"
- `##cdo [(alias OR template number) list separated with space OR nothing]`, means "**c**omment out this block of code for **d**iff **o**nly"
- `##s [alias] [template number]`, means "**s**et alias to template number"

Example usage:

```
##s undrfined 10 (set alias "undrfined" to template number 10. don't forget to update it tho!)

##do undrfined Vlad 111 (use this code block only when diffing with undrfined or Vlad or template#111)
@datetime: //body/time
published_date: $@
##? (means else, do this block for every other diff)
published_date: //meta[@property="date"]/@content
##
```

ivdiff will automatically comment out all the code when you'll start diffing with other template.

## ivdiff.py#compare()

You can use this method if you want to remove some elements that exist in one template but are missing in another. Or you can convert them somehow to match other contestant's template.

## Linux & Mac OS

..are not supported because I didn't test it there 🤷‍♂️

# Delayed [issues] service

Sends issue in the last second. Yeah, shame on me!
Install `delayed_userscript.js` in the tampermonkey, then run service itself: `py delayed_service.py`.

## It's not only about evil

Delayed service actually has a lot more useful features. I don't remember any of them though, so that would be a surprise for you :)

