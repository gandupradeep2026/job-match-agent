import re
import unicodedata
from urllib.parse import quote_plus, urlparse

import streamlit as st


# ==================================================
# HELPER FOR PORTAL DEFINITIONS
# ==================================================

def portal(name, url, portal_type):
    return {
        "name": name,
        "url": url,
        "type": portal_type,
    }


# ==================================================
# JOB PORTAL DATABASE
# ==================================================

JOB_PORTALS = {
    "Germany": [
        portal(
            "Bundesagentur für Arbeit",
            "https://www.arbeitsagentur.de/jobsuche/",
            "Official",
        ),
        portal(
            "StepStone Germany",
            "https://www.stepstone.de/",
            "General",
        ),
        portal(
            "Indeed Germany",
            "https://de.indeed.com/",
            "General",
        ),
        portal(
            "LinkedIn Jobs",
            "https://www.linkedin.com/jobs/",
            "Professional Network",
        ),
        portal(
            "XING Jobs",
            "https://www.xing.com/jobs",
            "Professional Network",
        ),
        portal(
            "EURES",
            "https://eures.europa.eu/",
            "European",
        ),
        portal(
            "meinestadt.de Jobs",
            "https://jobs.meinestadt.de/",
            "General / Local",
        ),
        portal(
            "JobMESH",
            "https://jobmesh.de/",
            "General",
        ),
        portal(
            "Workwise",
            "https://www.workwise.io/",
            "Professional",
        ),
        portal(
            "jobvector",
            "https://www.jobvector.de/",
            "Tech / Engineering",
        ),
    ],

    "Austria": [
        portal(
            "AMS eJob-Room",
            "https://jobroom.ams.or.at/",
            "Official",
        ),
        portal(
            "karriere.at",
            "https://www.karriere.at/jobs",
            "General",
        ),
        portal(
            "StepStone Austria",
            "https://www.stepstone.at/",
            "General",
        ),
        portal(
            "Indeed Austria",
            "https://at.indeed.com/",
            "General",
        ),
        portal(
            "LinkedIn Jobs",
            "https://www.linkedin.com/jobs/",
            "Professional Network",
        ),
        portal(
            "XING Jobs",
            "https://www.xing.com/jobs/t-%C3%B6sterreich",
            "Professional Network",
        ),
        portal(
            "EURES",
            "https://eures.europa.eu/",
            "European",
        ),
        portal(
            "Work in Austria",
            "https://www.workinaustria.com/en/",
            "International",
        ),
        portal(
            "DEVjobs.at",
            "https://devjobs.at/",
            "Tech",
        ),
        portal(
            "hokify",
            "https://hokify.at/jobs",
            "General",
        ),
    ],

    "Switzerland": [
        portal(
            "jobs.ch",
            "https://www.jobs.ch/en/",
            "General",
        ),
        portal(
            "JobScout24",
            "https://www.jobscout24.ch/en/",
            "General",
        ),
        portal(
            "jobup.ch",
            "https://www.jobup.ch/en/",
            "General",
        ),
        portal(
            "Job-Room / arbeit.swiss",
            "https://www.job-room.ch/",
            "Official",
        ),
        portal(
            "Indeed Switzerland",
            "https://ch.indeed.com/",
            "General",
        ),
        portal(
            "LinkedIn Jobs",
            "https://www.linkedin.com/jobs/",
            "Professional Network",
        ),
        portal(
            "XING Jobs",
            "https://www.xing.com/jobs",
            "Professional Network",
        ),
        portal(
            "EURES",
            "https://eures.europa.eu/",
            "European",
        ),
        portal(
            "SwissDevJobs",
            "https://swissdevjobs.ch/",
            "Tech",
        ),
        portal(
            "ICTcareer",
            "https://www.ictcareer.ch/",
            "IT / Tech",
        ),
    ],

    "France": [
        portal(
            "France Travail",
            "https://candidat.francetravail.fr/offres/recherche",
            "Official",
        ),
        portal(
            "APEC",
            "https://www.apec.fr/",
            "Professional",
        ),
        portal(
            "Welcome to the Jungle",
            "https://www.welcometothejungle.com/fr/jobs",
            "Professional / Tech",
        ),
        portal(
            "Indeed France",
            "https://fr.indeed.com/",
            "General",
        ),
        portal(
            "LinkedIn Jobs",
            "https://www.linkedin.com/jobs/",
            "Professional Network",
        ),
        portal(
            "HelloWork",
            "https://www.hellowork.com/fr-fr/emploi.html",
            "General",
        ),
        portal(
            "Meteojob",
            "https://www.meteojob.com/",
            "General",
        ),
        portal(
            "Cadremploi",
            "https://www.cadremploi.fr/",
            "Professional",
        ),
        portal(
            "LesJeudis",
            "https://www.lesjeudis.com/",
            "IT / Tech",
        ),
        portal(
            "Talent.com France",
            "https://fr.talent.com/",
            "Job Search Engine",
        ),
    ],

    "United Kingdom": [
        portal(
            "GOV.UK Find a Job",
            "https://www.gov.uk/find-a-job",
            "Official",
        ),
        portal(
            "Indeed UK",
            "https://uk.indeed.com/",
            "General",
        ),
        portal(
            "LinkedIn Jobs",
            "https://www.linkedin.com/jobs/",
            "Professional Network",
        ),
        portal(
            "Reed",
            "https://www.reed.co.uk/jobs",
            "General",
        ),
        portal(
            "Totaljobs",
            "https://www.totaljobs.com/",
            "General",
        ),
        portal(
            "CV-Library",
            "https://www.cv-library.co.uk/",
            "General",
        ),
        portal(
            "Glassdoor UK",
            "https://www.glassdoor.co.uk/Job/index.htm",
            "Jobs / Company Research",
        ),
        portal(
            "Adzuna UK",
            "https://www.adzuna.co.uk/",
            "Job Search Engine",
        ),
        portal(
            "Jora UK",
            "https://uk.jora.com/",
            "Job Search Engine",
        ),
        portal(
            "CWJobs",
            "https://www.cwjobs.co.uk/",
            "IT / Tech",
        ),
    ],

    "Sweden": [
        portal(
            "Platsbanken",
            "https://arbetsformedlingen.se/platsbanken/",
            "Official",
        ),
        portal(
            "JobbSafari",
            "https://jobbsafari.se/",
            "General",
        ),
        portal(
            "Jobbland",
            "https://jobbland.se/",
            "General",
        ),
        portal(
            "Ledigajobb.se",
            "https://ledigajobb.se/",
            "General",
        ),
        portal(
            "Indeed Sweden",
            "https://se.indeed.com/",
            "General",
        ),
        portal(
            "LinkedIn Jobs",
            "https://www.linkedin.com/jobs/",
            "Professional Network",
        ),
        portal(
            "EURES",
            "https://eures.europa.eu/",
            "European",
        ),
        portal(
            "The Hub",
            "https://thehub.io/jobs",
            "Startups / Tech",
        ),
        portal(
            "Academic Work",
            "https://www.academicwork.se/lediga-jobb",
            "Graduate / Professional",
        ),
        portal(
            "The Local Jobs",
            "https://www.thelocal.se/jobs/",
            "International",
        ),
    ],

    "Norway": [
        portal(
            "NAV Arbeidsplassen",
            "https://arbeidsplassen.nav.no/",
            "Official",
        ),
        portal(
            "FINN Jobs",
            "https://www.finn.no/job/",
            "General",
        ),
        portal(
            "Jobbnorge",
            "https://www.jobbnorge.no/search/en",
            "Professional / Public",
        ),
        portal(
            "JobbSafari Norway",
            "https://www.jobbsafari.no/",
            "General",
        ),
        portal(
            "Indeed Norway",
            "https://no.indeed.com/",
            "General",
        ),
        portal(
            "LinkedIn Jobs",
            "https://www.linkedin.com/jobs/",
            "Professional Network",
        ),
        portal(
            "EURES",
            "https://eures.europa.eu/",
            "European",
        ),
        portal(
            "The Hub",
            "https://thehub.io/jobs",
            "Startups / Tech",
        ),
        portal(
            "KarriereStart",
            "https://karrierestart.no/",
            "Graduate / Professional",
        ),
        portal(
            "Jobs in Oslo",
            "https://www.jobsinoslo.com/",
            "International",
        ),
    ],

    "Denmark": [
        portal(
            "Jobindex",
            "https://www.jobindex.dk/",
            "General",
        ),
        portal(
            "Jobnet",
            "https://jobnet.dk/",
            "Official",
        ),
        portal(
            "Workindenmark",
            "https://www.workindenmark.dk/",
            "Official / International",
        ),
        portal(
            "Indeed Denmark",
            "https://dk.indeed.com/",
            "General",
        ),
        portal(
            "LinkedIn Jobs",
            "https://www.linkedin.com/jobs/",
            "Professional Network",
        ),
        portal(
            "The Hub",
            "https://thehub.io/jobs",
            "Startups / Tech",
        ),
        portal(
            "Graduateland",
            "https://graduateland.com/",
            "Graduate",
        ),
        portal(
            "Jobfinder",
            "https://www.jobfinder.dk/",
            "Professional",
        ),
        portal(
            "Jobs in Copenhagen",
            "https://www.jobsincopenhagen.com/",
            "International",
        ),
        portal(
            "StepStone Denmark",
            "https://www.stepstone.dk/",
            "General",
        ),
    ],

    "Finland": [
        portal(
            "Job Market Finland",
            "https://tyomarkkinatori.fi/en/personal-customers/vacancies",
            "Official",
        ),
        portal(
            "Work in Finland",
            "https://www.workinfinland.com/en/open-jobs/",
            "Official / International",
        ),
        portal(
            "Duunitori",
            "https://duunitori.fi/tyopaikat",
            "General",
        ),
        portal(
            "Jobly",
            "https://www.jobly.fi/en/jobs",
            "General",
        ),
        portal(
            "Indeed Finland",
            "https://fi.indeed.com/",
            "General",
        ),
        portal(
            "LinkedIn Jobs",
            "https://www.linkedin.com/jobs/",
            "Professional Network",
        ),
        portal(
            "EURES",
            "https://eures.europa.eu/",
            "European",
        ),
        portal(
            "Jobs in Finland",
            "https://jobsfinland.fi/",
            "International",
        ),
        portal(
            "The Hub",
            "https://thehub.io/jobs",
            "Startups / Tech",
        ),
        portal(
            "Academic Work Finland",
            "https://www.academicwork.fi/avoimet-tyopaikat",
            "Graduate / Professional",
        ),
    ],

    "Iceland": [
        portal(
            "Alfred",
            "https://alfred.is/",
            "General",
        ),
        portal(
            "Directorate of Labour",
            "https://island.is/en/o/directorate-of-labour",
            "Official",
        ),
        portal(
            "Job.is",
            "https://www.job.is/",
            "General",
        ),
        portal(
            "EURES",
            "https://eures.europa.eu/",
            "European",
        ),
        portal(
            "LinkedIn Jobs",
            "https://www.linkedin.com/jobs/",
            "Professional Network",
        ),
        portal(
            "Tvinna",
            "https://tvinna.is/",
            "Tech",
        ),
        portal(
            "Storf",
            "https://storf.is/",
            "General",
        ),
        portal(
            "Work in Iceland",
            "https://work.iceland.is/working/job-hunting/",
            "International",
        ),
        portal(
            "Intellecta",
            "https://intellecta.is/",
            "Recruitment",
        ),
        portal(
            "Indeed",
            "https://www.indeed.com/",
            "International",
        ),
    ],

    "Canada": [
        portal(
            "Job Bank Canada",
            "https://www.jobbank.gc.ca/jobsearch/",
            "Official",
        ),
        portal(
            "Indeed Canada",
            "https://ca.indeed.com/",
            "General",
        ),
        portal(
            "LinkedIn Jobs",
            "https://www.linkedin.com/jobs/",
            "Professional Network",
        ),
        portal(
            "Glassdoor Canada",
            "https://www.glassdoor.ca/Job/index.htm",
            "Jobs / Company Research",
        ),
        portal(
            "Workopolis",
            "https://www.workopolis.com/",
            "General",
        ),
        portal(
            "Eluta",
            "https://www.eluta.ca/",
            "Job Search Engine",
        ),
        portal(
            "Jobillico",
            "https://www.jobillico.com/",
            "General",
        ),
        portal(
            "Talent.com Canada",
            "https://ca.talent.com/",
            "Job Search Engine",
        ),
        portal(
            "CareerBeacon",
            "https://www.careerbeacon.com/",
            "General",
        ),
        portal(
            "Jobboom",
            "https://www.jobboom.com/",
            "General / Quebec",
        ),
    ],

    "United States": [
        portal(
            "Indeed",
            "https://www.indeed.com/",
            "General",
        ),
        portal(
            "LinkedIn Jobs",
            "https://www.linkedin.com/jobs/",
            "Professional Network",
        ),
        portal(
            "USAJOBS",
            "https://www.usajobs.gov/",
            "Federal Government",
        ),
        portal(
            "ZipRecruiter",
            "https://www.ziprecruiter.com/jobs",
            "General",
        ),
        portal(
            "Glassdoor",
            "https://www.glassdoor.com/Job/",
            "Jobs / Company Research",
        ),
        portal(
            "Dice",
            "https://www.dice.com/jobs",
            "IT / Tech",
        ),
        portal(
            "Wellfound",
            "https://wellfound.com/jobs",
            "Startups / Tech",
        ),
        portal(
            "FlexJobs",
            "https://www.flexjobs.com/",
            "Remote / Flexible",
        ),
        portal(
            "Snagajob",
            "https://www.snagajob.com/",
            "Hourly / Service",
        ),
        portal(
            "Handshake",
            "https://joinhandshake.com/",
            "Students / Graduates",
        ),
    ],

    "Australia": [
        portal(
            "SEEK Australia",
            "https://www.seek.com.au/",
            "General",
        ),
        portal(
            "Workforce Australia",
            "https://www.workforceaustralia.gov.au/individuals/jobs",
            "Official",
        ),
        portal(
            "Indeed Australia",
            "https://au.indeed.com/",
            "General",
        ),
        portal(
            "LinkedIn Jobs",
            "https://www.linkedin.com/jobs/",
            "Professional Network",
        ),
        portal(
            "Jora Australia",
            "https://au.jora.com/",
            "Job Search Engine",
        ),
        portal(
            "CareerOne",
            "https://www.careerone.com.au/",
            "General",
        ),
        portal(
            "Adzuna Australia",
            "https://www.adzuna.com.au/",
            "Job Search Engine",
        ),
        portal(
            "EthicalJobs",
            "https://www.ethicaljobs.com.au/",
            "Nonprofit / Social Impact",
        ),
        portal(
            "GradConnection",
            "https://au.gradconnection.com/",
            "Graduate",
        ),
        portal(
            "Sidekicker",
            "https://sidekicker.com/au/",
            "Casual / Hospitality",
        ),
    ],

    "New Zealand": [
        portal(
            "SEEK New Zealand",
            "https://www.seek.co.nz/",
            "General",
        ),
        portal(
            "Trade Me Jobs",
            "https://www.trademe.co.nz/a/jobs",
            "General",
        ),
        portal(
            "Indeed New Zealand",
            "https://nz.indeed.com/",
            "General",
        ),
        portal(
            "LinkedIn Jobs",
            "https://www.linkedin.com/jobs/",
            "Professional Network",
        ),
        portal(
            "Jora New Zealand",
            "https://nz.jora.com/",
            "Job Search Engine",
        ),
        portal(
            "JOBSPACE",
            "https://www.jobspace.co.nz/",
            "General",
        ),
        portal(
            "New Zealand Government Jobs",
            "https://jobs.govt.nz/",
            "Government",
        ),
        portal(
            "Student Job Search",
            "https://www.sjs.co.nz/",
            "Students / Part-Time",
        ),
        portal(
            "Adzuna New Zealand",
            "https://www.adzuna.co.nz/",
            "Job Search Engine",
        ),
        portal(
            "Kiwi Health Jobs",
            "https://www.kiwihealthjobs.com/",
            "Healthcare",
        ),
    ],
}


# ==================================================
# COUNTRY GROUPS
# ==================================================

COUNTRY_GROUPS = {
    "Central Europe": [
        "Germany",
        "Austria",
        "Switzerland",
        "France",
        "United Kingdom",
    ],
    "Nordic Countries": [
        "Sweden",
        "Norway",
        "Denmark",
        "Finland",
        "Iceland",
    ],
    "North America": [
        "Canada",
        "United States",
    ],
    "Oceania": [
        "Australia",
        "New Zealand",
    ],
}


# ==================================================
# URL HELPERS
# ==================================================

def make_slug(text):
    """
    Convert text into a URL-friendly path.

    Example:
        "Cloud Data Engineer" -> "cloud-data-engineer"
        "New York" -> "new-york"
    """

    text = unicodedata.normalize(
        "NFKD",
        text,
    )

    text = text.encode(
        "ascii",
        "ignore",
    ).decode(
        "ascii"
    )

    text = text.lower().strip()

    text = re.sub(
        r"[^a-z0-9]+",
        "-",
        text,
    )

    return text.strip("-")


def get_country_options():
    """
    Return all configured countries.
    """

    return list(
        JOB_PORTALS.keys()
    )


# ==================================================
# SMART SEARCH URL BUILDER
# ==================================================

def build_search_url(
    portal_data,
    country,
    job_title,
    location,
):
    """
    Build a direct job-search URL where a stable
    search URL pattern is available.

    If a direct-search pattern is not configured,
    return the normal portal homepage.
    """

    base_url = portal_data["url"]
    portal_name = portal_data["name"]

    job_title = job_title.strip()
    location = location.strip()

    # ----------------------------------------------
    # NO JOB TITLE
    # ----------------------------------------------

    if not job_title:
        return base_url, False

    # Use selected country when city is empty.

    search_location = (
        location
        if location
        else country
    )

    encoded_job = quote_plus(
        job_title
    )

    encoded_location = quote_plus(
        search_location
    )

    job_slug = make_slug(
        job_title
    )

    location_slug = make_slug(
        search_location
    )

    parsed_url = urlparse(
        base_url
    )

    domain = parsed_url.netloc.lower()

    # ==============================================
    # LINKEDIN
    # ==============================================

    if portal_name == "LinkedIn Jobs":
        return (
            "https://www.linkedin.com/jobs/search/"
            f"?keywords={encoded_job}"
            f"&location={encoded_location}",
            True,
        )

    # ==============================================
    # INDEED
    # Works with the regional Indeed domains.
    # ==============================================

    if "indeed." in domain:
        indeed_base = (
            f"{parsed_url.scheme}://"
            f"{parsed_url.netloc}"
        )

        return (
            f"{indeed_base}/jobs"
            f"?q={encoded_job}"
            f"&l={encoded_location}",
            True,
        )

    # ==============================================
    # GERMANY - BUNDESAGENTUR FÜR ARBEIT
    # ==============================================

    if portal_name == "Bundesagentur für Arbeit":
        return (
            "https://www.arbeitsagentur.de/"
            "jobsuche/suche"
            f"?angebotsart=1"
            f"&was={encoded_job}"
            f"&wo={encoded_location}",
            True,
        )

    # ==============================================
    # STEPSTONE GERMANY
    # ==============================================

    if portal_name == "StepStone Germany":
        return (
            "https://www.stepstone.de/jobs/"
            f"{job_slug}/in-{location_slug}",
            True,
        )

    # ==============================================
    # SEEK AUSTRALIA
    # ==============================================

    if portal_name == "SEEK Australia":

        if location:
            return (
                "https://www.seek.com.au/"
                f"{job_slug}-jobs/"
                f"in-{location_slug}",
                True,
            )

        return (
            "https://www.seek.com.au/"
            f"{job_slug}-jobs",
            True,
        )

    # ==============================================
    # SEEK NEW ZEALAND
    # ==============================================

    if portal_name == "SEEK New Zealand":

        if location:
            return (
                "https://www.seek.co.nz/"
                f"{job_slug}-jobs/"
                f"in-{location_slug}",
                True,
            )

        return (
            "https://www.seek.co.nz/"
            f"{job_slug}-jobs",
            True,
        )

    # ==============================================
    # REED UK
    # ==============================================

    if portal_name == "Reed":

        if location:
            return (
                "https://www.reed.co.uk/jobs/"
                f"{job_slug}-jobs-in-"
                f"{location_slug}",
                True,
            )

        return (
            "https://www.reed.co.uk/jobs/"
            f"{job_slug}-jobs",
            True,
        )

    # ==============================================
    # TOTALJOBS UK
    # ==============================================

    if portal_name == "Totaljobs":

        if location:
            return (
                "https://www.totaljobs.com/jobs/"
                f"{job_slug}/in-{location_slug}",
                True,
            )

        return (
            "https://www.totaljobs.com/jobs/"
            f"{job_slug}",
            True,
        )

    # ==============================================
    # JORA
    # ==============================================

    if portal_name in {
        "Jora UK",
        "Jora Australia",
        "Jora New Zealand",
    }:
        jora_base = (
            f"{parsed_url.scheme}://"
            f"{parsed_url.netloc}"
        )

        return (
            f"{jora_base}/j"
            f"?q={encoded_job}"
            f"&l={encoded_location}",
            True,
        )

    # ==============================================
    # USAJOBS
    # ==============================================

    if portal_name == "USAJOBS":
        return (
            "https://www.usajobs.gov/"
            "Search/Results"
            f"?k={encoded_job}"
            f"&l={encoded_location}",
            True,
        )

    # ==============================================
    # DICE
    # ==============================================

    if portal_name == "Dice":
        return (
            "https://www.dice.com/jobs"
            f"?q={encoded_job}"
            f"&location={encoded_location}",
            True,
        )

    # ==============================================
    # ZIPRECRUITER
    # ==============================================

    if portal_name == "ZipRecruiter":
        return (
            "https://www.ziprecruiter.com/"
            "jobs-search"
            f"?search={encoded_job}"
            f"&location={encoded_location}",
            True,
        )

    # ==============================================
    # NAV NORWAY
    # ==============================================

    if portal_name == "NAV Arbeidsplassen":
        return (
            "https://arbeidsplassen.nav.no/"
            "stillinger"
            f"?q={encoded_job}",
            True,
        )

    # ==============================================
    # DUUNITORI FINLAND
    # ==============================================

    if portal_name == "Duunitori":
        return (
            "https://duunitori.fi/"
            "tyopaikat"
            f"?haku={encoded_job}",
            True,
        )

    # ==============================================
    # FALLBACK
    # ==============================================
    #
    # Some portals use internal IDs, JavaScript,
    # session data or frequently changing URL formats.
    #
    # We deliberately open the portal homepage rather
    # than generate an unreliable/broken search URL.
    # ==============================================

    return base_url, False


# ==================================================
# PORTAL CARD
# ==================================================

def render_portal(
    portal_data,
    country,
    job_title,
    location,
):
    """
    Render one portal card.
    """

    search_url, direct_search = (
        build_search_url(
            portal_data=portal_data,
            country=country,
            job_title=job_title,
            location=location,
        )
    )

    st.markdown(
        f"### {portal_data['name']}"
    )

    if direct_search and job_title:
        st.caption(
            f"{portal_data['type']} • "
            "Direct search"
        )
    else:
        st.caption(
            f"{portal_data['type']} • "
            "Portal homepage"
        )

    if direct_search and job_title:

        button_label = (
            f"Search {job_title} ↗"
        )

    else:

        button_label = (
            "Open Job Portal ↗"
        )

    st.link_button(
        button_label,
        search_url,
        width="stretch",
    )


# ==================================================
# MAIN UI
# ==================================================

def render_job_portals():

    st.header(
        "🌍 International Job Portals"
    )

    st.write(
        "Select your target country, "
        "enter the job you are looking for, "
        "and optionally enter a city or region."
    )

    # ==================================================
    # SEARCH INPUTS
    # ==================================================

    country = st.selectbox(
        "Target country",
        get_country_options(),
        key="job_portals_country",
    )

    input_col1, input_col2 = (
        st.columns(2)
    )

    with input_col1:

        job_title = st.text_input(
            "Job title or keywords",
            placeholder=(
                "e.g. Data Engineer"
            ),
            key="job_portals_job_title",
        )

    with input_col2:

        location = st.text_input(
            "City or region",
            placeholder=(
                "e.g. Berlin"
            ),
            key="job_portals_location",
        )

    # ==================================================
    # SEARCH SUMMARY
    # ==================================================

    if job_title:

        if location:

            st.success(
                f"Searching for "
                f"**{job_title}** jobs in "
                f"**{location}, {country}**."
            )

        else:

            st.success(
                f"Searching for "
                f"**{job_title}** jobs in "
                f"**{country}**."
            )

    else:

        st.info(
            "Enter a job title above to activate "
            "direct job searches where supported."
        )

    portals = JOB_PORTALS.get(
        country,
        [],
    )

    st.divider()

    # ==================================================
    # RESULTS HEADING
    # ==================================================

    st.subheader(
        f"Recommended Job Portals — {country}"
    )

    st.caption(
        f"{len(portals)} recommended portals"
    )

    if not portals:

        st.warning(
            "No job portals are configured "
            "for this country."
        )

        return

    # ==================================================
    # PORTALS - TWO COLUMNS
    # ==================================================

    for index in range(
        0,
        len(portals),
        2,
    ):

        left_column, right_column = (
            st.columns(2)
        )

        with left_column:

            render_portal(
                portal_data=portals[index],
                country=country,
                job_title=job_title,
                location=location,
            )

        if index + 1 < len(portals):

            with right_column:

                render_portal(
                    portal_data=portals[index + 1],
                    country=country,
                    job_title=job_title,
                    location=location,
                )

    # ==================================================
    # REGION
    # ==================================================

    st.divider()

    for (
        group_name,
        countries,
    ) in COUNTRY_GROUPS.items():

        if country in countries:

            st.caption(
                f"Region: {group_name}"
            )

            break

    # ==================================================
    # USER NOTE
    # ==================================================

    st.caption(
        "Direct search is used only where a reliable "
        "search URL is available. Other buttons open "
        "the portal homepage so that broken search "
        "links are avoided."
    )