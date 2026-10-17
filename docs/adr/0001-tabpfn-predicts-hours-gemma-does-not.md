# TabPFN predicts hours; Gemma does not

A Quote is a number someone will send to a client. If Gemma (or any language model) is allowed to pick that number, the product is a chatbot with extra steps, and client briefs plus past fees become training-data leakage in prose.

We split the work: Gemma may only emit a Feature Row (kind, screens, integrations, revisions, deadline, repeat). TabPFN-3.5 fits on History and predicts hours. Code turns hours into a fee using the freelancer's own realized hourly rate. A Number Guard rejects any prose whose digits are not in that TabPFN output.

The alternative was a single Gemma prompt that "looks at the CSV and writes a quote." That is easier to demo and impossible to audit. We rejected it because the open piece that actually works on 20–40 rows is TabPFN, and because a hallucinated rupee amount is how this side hustle would lose its first user.
