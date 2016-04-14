#!/usr/bin/env python
import sys
from argparse import ArgumentParser
from collections import defaultdict
from lxml import html
import urlparse


def _form_score(form):
    score = 0
    # In case of user/pass or user/pass/remember-me
    if len(form.inputs.keys()) in (2, 3):
        score += 10

    typecount = defaultdict(int)
    for x in form.inputs:
        type_ = x.type if isinstance(x, html.InputElement) else "other"
        typecount[type_] += 1

    if typecount['text'] > 1:
        score += 10
    if not typecount['text']:
        score -= 10

    if typecount['password'] == 1:
        score += 10
    if not typecount['password']:
        score -= 10

    if typecount['checkbox'] > 1:
        score -= 10
    if typecount['radio']:
        score -= 10

    return score


def _pick_form(forms):
    """Return the form most likely to be a login form"""
    return sorted(forms, key=_form_score, reverse=True)[0]


def _pick_fields(form):
    userfield = passfield = emailfield = None
    for x in form.inputs:
        if not isinstance(x, html.InputElement):
            continue

        type_ = x.type
        if type_ == 'password' and passfield is None:
            passfield = x.name
        elif type_ == 'text' and userfield is None:
            userfield = x.name
        elif type_ == 'email' and emailfield is None:
            emailfield = x.name

    return userfield or emailfield, passfield


def submit_value(form):
    """Returns the value for the submit input, if any"""
    hasSubmitBefore = False
    for x in form.inputs:
        if hasattr(x,'type') and x.type == "submit":
            if x.name:
                return hasSubmitBefore,[(x.name, x.value)]
            hasSubmitBefore = True
    else:
        return hasSubmitBefore,[]

def url_processor(self, url):
    try:
        parsed_url = urlparse(url)
        path = parsed_url.path
        protocol = parsed_url.scheme + '://'
        hostname = parsed_url.hostname
        netloc = parsed_url.netloc
        doc_domain = '.'.join(hostname.split('.')[-2:])
    except:
        self.log('Could not parse url: ' + url)
        return

    return (netloc, protocol, doc_domain, path)


def fill_login_form(url, body, username, password):
    doc = html.document_fromstring(body, base_url=url)
    form = _pick_form(doc.xpath('//form'))
    userfield, passfield = _pick_fields(form)
    form.fields[userfield] = username
    form.fields[passfield] = password
    hasSubmitBefore, submit_values= submit_value(form)
    form_values = form.form_values()
    if not hasSubmitBefore:
        form_values += submit_values
    return (form.form_values()+submit_values),form_values, form.action or form.base_url, form.method, _pick_fields(form)
