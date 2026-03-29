import os
import chromadb

def seed_database():
    print("Initializing ChromaDB persistent client at 'chroma_store/'...")
    
    # Ensure the store path is in the project root
    store_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_store")
    client = chromadb.PersistentClient(path=store_path)
    
    print("Creating or retrieving collection 'dhan_i_knowledge'...")
    collection = client.get_or_create_collection(name="dhan_i_knowledge")
    
    # 20 realistic paragraph-length text snippets covering user specs
    documents = [
        "Under Section 80C of the Income Tax Act, you can claim a maximum deduction of Rs. 1.5 lakh per financial year. This includes investments in Equity Linked Savings Schemes (ELSS), Public Provident Fund (PPF), Life Insurance Corporation (LIC) premiums, and 5-year fixed deposits.",
        "Section 80CCD(1B) provides an exclusive additional tax deduction of up to Rs. 50,000 for investments made in the National Pension System (NPS). This is over and above the Rs. 1.5 lakh limit available under Section 80C, making it a great tool for retirement planning.",
        "Long Term Capital Gains (LTCG) tax on equity and equity-oriented mutual funds is applicable at a flat rate of 10% without indexation, but only if your total gains exceed Rs. 1 lakh in a financial year. Gains up to Rs. 1 lakh are completely tax-free.",
        "Short Term Capital Gains (STCG) tax applies when you sell equity shares or equity mutual funds within one year of buying them. The STCG tax rate is currently a flat 15% on whatever profit you have made.",
        "SEBI has made it mandatory for all individuals to complete their KYC (Know Your Customer) process before making any mutual fund investments. This involves verifying your identity and address using PAN and Aadhaar.",
        "A Systematic Investment Plan (SIP) allows you to invest a fixed amount regularly in mutual funds. It benefits from 'rupee cost averaging', meaning you buy more units when the market is down and fewer units when the market is high, lowering your average cost per unit over time.",
        "Direct mutual fund plans are bought directly from the fund house, while regular plans are bought through a broker or distributor. Direct plans have a lower expense ratio because there are no distributor commissions involved, leading to higher long-term returns for the investor.",
        "Term insurance is a pure life cover that offers a high death benefit at a very low premium but has no maturity value. In contrast, Unit Linked Insurance Plans (ULIPs) mix insurance with investment, meaning they have higher premiums and complex charges, but offer some return if you survive the policy term.",
        "A standard rule of thumb for financial stability is to maintain an emergency fund equal to at least 6 months of your mandatory living expenses. This fund should be kept in highly liquid instruments like savings accounts or liquid mutual funds for immediate access during job loss or medical emergencies.",
        "The debt snowball method is a strategy to get out of debt quickly. You list all your loans from smallest to largest balance, regardless of interest rate. You pay minimums on all, but throw every extra rupee at the smallest loan until it's cleared, gaining psychological momentum.",
        "Under Section 80D, you can claim tax deductions for health insurance premiums paid for yourself, your spouse, and dependent children up to Rs. 25,000, and an additional Rs. 50,000 for senior citizen parents.",
        "Sovereign Gold Bonds (SGBs) are government securities denominated in grams of gold. Besides reflecting the market price of gold, they pay a fixed interest of 2.5% per annum on the initial investment, making them better than holding physical gold.",
        "Interest earned on Bank Fixed Deposits (FDs) is fully taxable as per your income tax slab. If the interest exceeds Rs. 40,000 in a year (Rs. 50,000 for senior citizens), the bank will deduct 10% TDS automatically unless you submit Form 15G/15H.",
        "The Voluntary Provident Fund (VPF) allows employees to contribute more than the mandatory 12% of their basic salary towards their EPF. VPF earns the same high, tax-free interest rate as EPF, making it a solid fixed-income investment.",
        "Credit cards typically offer an interest-free grace period of up to 45-50 days. If you pay your entire statement balance in full before the due date, you won't be charged any interest. However, carrying a balance incurs massive interest rates of 36% to 42% annually.",
        "Section 24(b) of the Income Tax Act allows a deduction of up to Rs. 2 lakh on the interest paid towards a home loan for a self-occupied property. This helps significantly reduce the effective interest rate of a mortgage.",
        "The Rule of 72 is a quick mental math formula to estimate how long an investment takes to double. Just divide 72 by the annual expected return percentage. For example, at an 8% return, your money doubles in 72 / 8 = 9 years.",
        "The 50-30-20 rule is a popular budgeting framework. It suggests allocating 50% of your after-tax income to absolute needs (rent, groceries), 30% to wants (dining out, entertainment), and strictly transferring 20% to savings and investments.",
        "Index funds are passive mutual funds that simply mimic a market index like the Nifty 50. Since they don't employ active fund managers to pick stocks, their expense ratios are extremely low, often outperforming active funds over a 10+ year horizon.",
        "The Employees' Provident Fund (EPF) is a retirement benefit scheme for salaried employees. Total deposits, interest earned, and the final withdrawal are all completely tax-exempt, giving it 'EEE' (Exempt-Exempt-Exempt) tax status."
    ]
    
    ids = [f"doc_{str(i).zfill(3)}" for i in range(len(documents))]
    
    print(f"Adding {len(documents)} documents to the vector space. Please wait...")
    
    # Render's free tier has an ephemeral filesystem, meaning the chroma_store/ directory 
    # gets completely wiped on every redeploy. This is handled automatically because the 
    # render.yaml buildCommand runs this seed script every time. No manual intervention 
    # is needed, but future developers should be aware this is why seeding is in the build step!
    
    # Add documents (Chroma automatically uses a sentence-transformer model to generate embeddings)
    collection.add(
        documents=documents,
        ids=ids
    )
    
    print("Database seeding completed successfully!! 🎉")

if __name__ == "__main__":
    seed_database()
