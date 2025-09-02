/* Example news data */
    const newsData = [
     { title: "Nextflix", description: "Netflix’s domestic subscriber base crossed the 45 million mark in 2016 with continued growth anticipated.", logo: "https://logo.clearbit.com/Netflix.com" },
    { title: "Amazon", description: "Amazon announces plans for AI to replace jobs CEO Andy Jassy said in a message to employees that Amazon “will need fewer people doing some of the jobs that are being done today” and will reduce its total corporate workforce in the next few years.", logo: "https://logo.clearbit.com/amazon.com" },
    { title: "Chevron Corporation", description: "Chevron reported disappointing results for Q4 2016, which they say is a reflection of the low oil and gas prices in 2016.", logo: "https://logo.clearbit.com/chevron.com" },
    { title: "Exxon Mobil Corporation", description: "Exxon said it will increase its 2017 capital spending program, which includes exploration, to an estimated $22 billion. In 2016, capital spending fell 38 percent to $19.3 billion.", logo: "https://logo.clearbit.com/exxonmobil.com" },
    { title: "Pfizer Inc.", description: "Pfizer, which closed its $14 billion acquisition of Medivation last September, reported a lower-than-expected profit, hit by lower demand for its flagship vaccine Prevnar and higher expenses.", logo: "https://logo.clearbit.com/pfizer.com" },
    { title: "Home Depot, Inc.", description: "Home Depot is coming off strong earnings to end the year with hopes of continuing the momentum in Q1.", logo: "https://logo.clearbit.com/homedepot.com" },
    { title: "Tootsie Roll Industries, Inc.", description: "Following lower than expected sales to end the year, Tootsie Roll hopes to get back on track this quarter.", logo: "https://logo.clearbit.com/tootsie.com" },
    { title: "The Kraft Heinz Company", description: "Kraft Heinz ended the year strong with cost cuts and looks to start the year with momentum.", logo: "https://www.perficient.com/-/media/images/logos/client-logos/kraft-heinz.ashx?h=200&iar=0&w=500&hash=DD4F19FA0DCECA2BF7C26B45B8C38E25" },
    { title: "Johnson & Johnson", description: "Johnson & Johnson announced sales of $18.1 billion for the fourth quarter of 2016, an increase of 1.7% as compared to the fourth quarter of 2015.", logo: "https://logo.clearbit.com/jnj.com" },
    { title: "General Motors Company", description: "GM sold a record 10 million vehicles globally in 2016, up just over 1 percent from the previous year. The results were helped by robust sales of its most profitable vehicles, trucks and SUVs.", logo: "https://logo.clearbit.com/gm.com" },
    { title: "Nike, Inc.", description: "Nike’s earnings got a boost from smaller selling and administrative expenses. Also, direct-to-consumer sales, which include Nike.com and its branded stores, shot 23 percent higher.", logo: "https://logo.clearbit.com/nike.com" },
    { title: "The Walt Disney Company", description: "Disney CEO said that great content is what will continue to drive opportunities and that Disney is well-positioned strategically.", logo: "https://logo.clearbit.com/disney.com" },
    { title: "Under Armour, Inc.", description: "There are rumors that Under Armour may be headed for a rough start to the year with concerns over their sales target.", logo: "https://logo.clearbit.com/underarmour.com" },
    { title: "Chipotle Mexican Grill, Inc.", description: "Chipotle expects sales to rebound in 2017 with simplified operations and digital marketing.", logo: "https://logo.clearbit.com/chipotle.com" },
    { title: "Starbucks Corp", description: "Starbucks mobile ordering success causes crowding issues and lower-than-expected growth.", logo: "https://logo.clearbit.com/starbucks.com" },
    { title: "McDonald's Corporation", description: "McDonald’s recently launched new Big Mac versions and ad campaigns to boost sales.", logo: "https://logo.clearbit.com/mcdonalds.com" },
    { title: "Ford Motor Company", description: "Ford sold 6.65 million new vehicles in 2016, close to 50% of which were sold in North America, which contributed close to 95% of the company's pre-tax profit.", logo: "https://logo.clearbit.com/ford.com" },
    { title: "Tesla, Inc.", description: "Tesla continues to innovate in the electric vehicle market, with plans to expand its Gigafactories globally.", logo: "https://logo.clearbit.com/tesla.com" },
    { title: "Facebook, Inc.", description: "Facebook focuses on expanding its metaverse initiatives while addressing privacy concerns.", logo: "https://logo.clearbit.com/facebook.com" },
    { title: "Rolls-Royce Holdings", description: "Rolls-Royce is investing in sustainable aviation technology to reduce its carbon footprint.", logo: "https://logo.clearbit.com/rolls-royce.com" },
    { title: "Samsung Electronics", description: "Samsung leads the smartphone market with its latest Galaxy series and innovations in foldable devices.", logo: "https://logo.clearbit.com/samsung.com" },
    { title: "Apple Inc.", description: "Apple has returned to growth as it sold more expensive iPhones, but the company’s future is less certain as they gave future guidance on the lower end of expectations.", logo: "https://logo.clearbit.com/apple.com" },
    { title: "Microsoft Corporation", description: "Microsoft focuses on cloud computing and AI advancements to maintain its competitive edge.", logo: "https://logo.clearbit.com/microsoft.com" },
    { title: "NVIDIA Corporation", description: "NVIDIA's GPUs remain at the forefront of gaming and AI technology.", logo: "https://logo.clearbit.com/nvidia.com" },
    {title: "Walmart Inc.", description: "Wal-Mart is coming off a strong quarter where earnings topped analyst expectations. They are investing heavily in e-commerce in hopes of growing revenue and competing with Amazon.", logo: "https://logo.clearbit.com/walmart.com" },
    {title:"Campbell's Soup", description: "It looks like it will be a volatile quarter for Campbell’s stock. As an investor, you may want to consider other options.", logo : "https://logo.clearbit.com/campbells.com" },
    {title: "Comcast", description: "It appears Comcast’s stock price will be on the rise during this quarter, but it may not outperform a broader index.", logo: "https://logo.clearbit.com/comcast.com" },
    { title: "Google LLC", description: "Google continues to dominate the search engine market while expanding its cloud services.", logo: "https://logo.clearbit.com/google.com" }
];

    const newsbox = document.getElementById('newsbox');
/* Function to render news cards */
    function renderNews(data) {
        newsbox.innerHTML = '';
        data.forEach(news => {
            const newsCard = `
                <div class="news-card">
                    <div class="news-logo">
                        <img src="${news.logo}" alt="${news.title}">
                    </div>
                    <div class="news-content">
                        <h2 class="news-title">${news.title}</h2>
                        <p class="news-description">${news.description}</p>
                    </div>
                </div>
            `;
            newsbox.innerHTML += newsCard;
        });
    }
/* Function to filter news based on search input */
    function filterNews() {
        const searchInput = document.getElementById('searchInput').value.toLowerCase();
        const filteredNews = newsData.filter(news =>
            news.title.toLowerCase().includes(searchInput) ||
            news.description.toLowerCase().includes(searchInput)
        );
        renderNews(filteredNews);
    }

    renderNews(newsData);
