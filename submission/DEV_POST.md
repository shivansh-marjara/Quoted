*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 2: Side Hustle](https://dev.to/challenges/hacktoberfest-week2-2026-10-12)*

# You said 10. It took 19.

A freelancer said yes because the job sounded small. Ten hours. It took nineteen. Pay arrived for ten. The rest was free, and that still stings — first year or tenth.

I did this on a small website. Eight thousand rupees. Nineteen hours. I didn't ask for the extra. Then the same people came back, and ten hours almost came out of my mouth again.

**Quoted** is the notebook I wanted that day. Not a chatbot making up a price. Promised hours on one line. Hours it really took on the next. Next time an ask lands, the cheap number has somewhere to get stuck.

Would someone pay Rs 499 a month so they never give the next week away? Maybe, if that week already went unpaid. I sat with my own live site and said no. I'll tell you why at the end. I won't invent a friend who said yes.

## What I Built

Finished work goes in first. What the client asked. Hours promised. Hours it took. What got paid, if that number is still around. Money can stay blank.

No file needed. Three jobs from memory is enough. A list works too — Excel, a photo of paper, a PDF, Word. Drop it.

Then a new ask arrives. Paste it. Press **What should I promise this time?**

Gemma reads the ask and may only write six facts: what kind of work, how many pages, extra tools, rounds of changes, how soon, and whether this person is known. Gemma does not pick hours. Gemma does not pick rupees. If a number sneaks into the sentence that didn't come from the notebook, the sentence gets thrown away.

TabPFN looks at finished jobs of that same kind. It's built for small tables, the size of a freelancer's year. Out comes a low, a middle, and a high. The middle, times what an hour actually earns, rounded to five hundred rupees. That's the number that can go in the reply.

If there aren't three jobs of that kind yet, the pad still doesn't blend a shop into a website. It follows the clinic. I learned that the hard way, below.

New or ten years in, the notebook starts empty. The example jobs sit behind a small door, marked as not yours.

## Demo

No account.

Live: [https://quoted-32zd.onrender.com](https://quoted-32zd.onrender.com)

Code: [https://github.com/shivansh-marjara/Quoted](https://github.com/shivansh-marjara/Quoted)

A minute on someone else's notebook, so TabPFN has a full table to chew:

1. Open **See how it looks with an example**.
2. Open **Or try a message they might send**, then **Dentist website by Friday**.
3. Press **What should I promise this time?**

You should see **19 hours** and **₹28,500**. Keep 3 hours. Don't promise less than 19.

That's the clean click. It uses TabPFN on the live site. If TabPFN is missing, similar finished jobs still fill the pad, and the pad says so.

The true first sit-down is not the dentist. It's three of my own jobs and a physio in Pune. That story is under **My First User**. There's a **Physio website by Friday** sample now, if you want the same ask.

## How I Built It

Gemma reads the ask and writes six facts. Never the money. This laptop has 4 GB of memory, so Gemma doesn't fit here. It runs at Google AI Studio. I'm saying that out loud. Open weights still matter: the reader can be swapped later. This post won't claim it runs on the machine when it doesn't.

TabPFN looks at hours that already happened. Model 3.5. It only steps in when there are enough jobs of the same kind. Otherwise analog uses the clinic, not the shop. The pad still fills with no key.

Then a check: every digit in the sentence has to come from those hours, the extra hours, the rate, or the fee. Two tries. After that, the raw numbers.

The same “look at jobs like this” idea was tested on a public set of old software projects (Desharnais, n=46). Mean MAE 3115. Linear 2014. Analog 1972. **TabPFN-3.5: 1618**, and it hit within 25% more often than the others. One later fold, TabPFN lost to a straight line (1096 vs 988). That row is in `eval/REPORT.md`. I'd rather show a loss than hide the table.

The site lives on Render. One box. The notebook on the screen and the brain behind it go out together. Open `/api/health` if you want to see TabPFN and Gemma are both on.

The screen looks like paper on purpose. This is a notebook, not a dashboard.

## Why Does Open Innovation Matter?

A year of clients does not belong in a locked chat just to get a guess. Those rows are names, hours, and what got paid.

I didn't keep the whole year off the internet. That's the honest bit. Finished jobs stay in the browser. The new ask still goes to Gemma so it can name the job — six facts, no rupees. A closed quote tool would guess the fee from the vibe, then bill every time, until you're renting your own memory.

TabPFN is open for a table this small. Fit on the jobs. Give a band. No “upload the whole story as a prompt.” Gemma is open too, so the reader isn't glued to one company. The money check only works because the hours come out as a short list of numbers. A chatbot has no such list. It just sounds sure.

That's why. Not because “open” looks good in a post. Because a sentence shouldn't invent ₹58,500 when the clinic took 16 hours.

## My Agent Session

I built this in Cursor. There's no DevRelay replay to embed. The work is the commits: [github.com/shivansh-marjara/Quoted/commits/main](https://github.com/shivansh-marjara/Quoted/commits/main).

## My First User

I asked freelancer friends to sit with this. They were busy. Inventing them would be a lie.

So the first sit-down was me. Three jobs. One new ask. Three questions.

- Clinic website. Said 10. Took 16. Gave away 6.
- Sari shop. Said 36. Took 48. Gave away 12.
- Coaching dashboard. Said 28. Took 40. Gave away 12.

The pad said **30 hours unpaid**. True. 6 and 12 and 12. For a second it felt like being seen.

Then a new person: a physiotherapist in Pune, a small website by Friday, five pages, WhatsApp, two rounds of changes, first time.

Quoted said: don't promise less than **39 hours**. Send **₹58,500**. It might take 15 to 51.

The last small site was 16 hours. 39 is not a small site. That hurt in a different way. I'd come for help. The help was too big.

Gemma had read “small website” as wiring, because of WhatsApp. TabPFN then mixed in the shop and the dashboard. A clinic quote inherited a shop's week.

I changed two things after that sit-down, and I'm leaving the miss in this post so the dentist click doesn't look like magic.

1. A website with a WhatsApp button is still a website.
2. Hours come from the same kind of finished job. One clinic and a shop is not a table of clinics.

Same three jobs. Same physio ask. The pad now says **16 hours**, like the clinic. Band 14 to 21. Keep 5. The shop's 48 stayed out of it.

Three questions, answered out loud.

1. **Would you pay Rs 499 a month?**  
   No. Not this month. The unpaid hours already tell the truth. I'd pay after I've sent two real quotes this way and they didn't blow up.

2. **What did it get wrong?**  
   First time: a small website became wiring. 39 hours and ₹58,500. Sixteen was the truth. The first load also sat on a blank red bar. I waited. A freelancer waiting on a quote already feels that wait.

3. **What do you want it to tell you next?**  
   Which jobs it used. Say it: this is like the clinic, not the shop. That's what the second sit-down does now.

If a real freelancer sits down before the deadline, their words go here instead. Until then, these are mine. The feeling is worth paying for. The first session was not. The second one was closer.

Open the pad anyway. Write three jobs. See unpaid hours in red. Then paste this week's ask. That's the product.

## Prize Categories

- Best Use of TabPFN
- Best Use of Gemma
- Best Use of Render
