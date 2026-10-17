*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 2: Side Hustle](https://dev.to/challenges/hacktoberfest-week2-2026-10-12)*

# You said 10. It took 19.

You know this feeling.

They said the job was small. You are a freelancer, so you said yes. You promised 10 hours. It took 19. You got paid for 10. The other hours were free. That hurts. Every freelancer has felt this. First year or tenth.

I felt it too. I quoted eight thousand rupees for a small website. It took nineteen hours. I did not ask for the extra. I just swallowed it. Then they asked again, and I almost said 10 a second time.

So I made **Quoted**. I am not a chatbot that invents a price. I am a notebook. You write what you promised. You write what it took. I remember. Next time they ask, I stop you.

If you have already given a week away, you might pay Rs 499 a month so you never give the next week away. I sat down with my own live site and asked myself if I would pay. I said no. Not this month. I will tell you that story at the end. I will not make up a friend who said yes.

## What I Built

You and I talk like this.

You tell me a job you already finished. What they asked you to do. Hours you promised. Hours it took. What they paid, if you remember. You can leave money blank.

You do not need a file. Three jobs from your head is enough. If you have a list — Excel, a photo of paper, a PDF, Word — you can drop it.

Then they send you a new ask. You paste it. You press **What should I promise this time?**

Here is the rule I will not break:

I let Gemma read the ask. Gemma may only say what kind of work it is, how many pages, extra tools, how many rounds of changes, how soon, and whether you know this person. Gemma does not pick hours. Gemma does not pick rupees. If a number sneaks into the sentence that did not come from your jobs, I throw the sentence away.

I let TabPFN look at your finished jobs. TabPFN is built for small tables, the size of a freelancer's year. It tells me how long a job like this really takes you: a low, a middle, a high. I take the middle, times what you actually earn in an hour, and I round to five hundred rupees. That is the number you can send.

If you are new, you start empty. If you have been at this ten years, you start empty too. Same notebook. The example jobs are behind a small door, and they say they are not yours.

## Demo

Come sit with me. No account.

Live: [https://quoted-32zd.onrender.com](https://quoted-32zd.onrender.com)

The code: [https://github.com/shivansh-marjara/Quoted](https://github.com/shivansh-marjara/Quoted)

If you only have a minute, do this.

1. Open **See how it looks with an example**.
2. Open **Or try a message they might send**, then **Dentist website by Friday**.
3. Press **What should I promise this time?**

You should see **19 hours** and **₹28,500**. Keep 3 hours for yourself. The line says: do not promise less than 19 hours.

That dentist click uses TabPFN on the live site. I checked. If TabPFN is missing, I still look at jobs like yours and I tell you I did. I will not pretend.

If you have three finished jobs of your own, type them. Paste what they asked this week. Press the same button. That is the real talk.

## How I Built It

I will keep this plain.

Gemma reads the ask and writes six facts. Never the money. My laptop has 4 GB of memory. It cannot hold Gemma. So Gemma runs at Google AI Studio. I am saying that out loud. Open weights still matter: I can swap the reader later. I am not going to write “it runs on my machine” when it does not.

TabPFN looks at the hours that already happened. Model 3.5. If there is no TabPFN key, I look at the same kind of job you already did. The pad still fills.

I test the sentence. Every digit has to come from those hours, the extra hours, your rate, or the fee. Twice it can try. Then I show the raw numbers.

I also tested “look at jobs like yours” on a public set of old software projects. Looking at similar jobs beat guessing the average, and beat a straight line. The table is in the repo. TabPFN’s row was empty until I had a key. I left it empty. I would rather show a hole than a fake number.

The site lives on Render. One box. The notebook you see and the brain behind it go out together. Open `/api/health` if you want to see that TabPFN and Gemma are both on.

The screen looks like paper on purpose. This is a notebook. It is not a dashboard.

## Why Does Open Innovation Matter?

You would not paste last year’s clients into a locked chat just to get a guess. Those rows are names, hours, and what they paid. That is your year.

A closed quote tool wants the ask, then bills you every time. After a month you are renting your own memory.

TabPFN is open for tables this small. Fit on my jobs. Give me a band. No “upload the whole story as a prompt.” Gemma is open too, so the reader is not glued to one company. The money check only works because the hours come out as a short list of numbers. A chatbot has no such list. It just sounds sure.

That is why I built it this way. Not because “open” looks good in a post. Because I cannot let a sentence invent ₹58,500 when your clinic took 16 hours.

## My Agent Session

I built this in Cursor. I do not have a pretty replay to paste. The GitHub repo is the work.

## My First User

I asked freelancer friends to sit with me. They were busy. I will not invent them.

So I sat with Quoted myself. Three jobs. One new ask. Three questions. Like I promised.

I wrote:

- Clinic website. I said 10. It took 16. I gave away 6.
- Sari shop. I said 36. It took 48. I gave away 12.
- Coaching dashboard. I said 28. It took 40. I gave away 12.

The pad said **30 hours unpaid**. That was true. 6 and 12 and 12. For a second I felt seen.

Then I pasted what a new person asked: a physiotherapist in Pune, a small website by Friday, five pages, WhatsApp, two rounds of changes, first time with them.

Quoted said: do not promise less than **39 hours**. Send **₹58,500**. It might take 15 to 51.

I sat there. My last small site was 16 hours. 39 is not a small site. That hurt in a different way. I had come for help, and the help was too big.

Gemma had read “small website” as a behind-the-scenes hookup. So TabPFN looked at the shop and the dashboard, not the clinic. That is on me to fix. I am writing it here so you do not think the demo is magic.

I asked myself the three questions. I answered out loud.

1. **Would you pay Rs 499 a month?**  
   No. Not this month. I would keep it open. I would pay after it talks about my clinic like a clinic, not like a shop.

2. **What did it get wrong?**  
   It called a small website a hookup. It told me 39 hours and ₹58,500. Sixteen was the truth. The first load also sat on a blank red bar. I waited. A freelancer waiting on a quote already feels that wait.

3. **What do you want it to tell you next?**  
   Which jobs you used. Say it to me: this is like your clinic, not your shop.

If a real freelancer sits with me before the deadline, I will put their words here instead. Until then, you have mine. The feeling is worth paying for. This one session was not.

I still think you should open the pad. Write three jobs. See your unpaid hours in red. That part already tells the truth. The next promise has to catch up.

## Prize Categories

- Best Use of TabPFN
- Best Use of Gemma
- Best Use of Render
