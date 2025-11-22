


import os
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun

# Set Google API key (ensure this is set in your environment or passed securely)
os.environ['GOOGLE_API_KEY'] = 'A**'

# Define Tools
import json
import requests

@tool
def search_properties(location: str = "Houston", min_price: int = 0, max_price: int = 10000000, min_area: int = 0, min_year: int = 0) -> str:
    """
    Search for properties using the SimplyRETS API.
    Args:
        location: City name (Note: Test API mainly has Houston data).
        min_price: Minimum price.
        max_price: Maximum price.
        min_area: Minimum square footage.
        min_year: Minimum year built.
    """
    print(f"Searching properties in {location} between {min_price} and {max_price}, >{min_area} sqft, built after {min_year}...")
    url = "https://api.simplyrets.com/properties"
    auth = ('simplyrets', 'simplyrets')
    params = {
        'q': location,
        'minprice': min_price,
        'maxprice': max_price,
        'minarea': min_area,
        'minyear': min_year,
        'limit': 5
    }
    try:
        response = requests.get(url, auth=auth, params=params)
        response.raise_for_status()
        data = response.json()
        results = []
        for prop in data:
            results.append({
                "id": prop.get('mlsId'),
                "title": f"{prop.get('property', {}).get('bedrooms')} Bed, {prop.get('property', {}).get('bathsFull')} Bath in {prop.get('address', {}).get('city')}",
                "location": prop.get('address', {}).get('full'),
                "price": prop.get('listPrice'),
                "features": f"{prop.get('property', {}).get('area')} sqft, {prop.get('property', {}).get('style')}, Built {prop.get('property', {}).get('yearBuilt')}",
                "image": prop.get('photos')[0] if prop.get('photos') else None
            })
        return json.dumps(results)
    except Exception as e:
        return json.dumps([{"error": f"Failed to fetch properties: {str(e)}"}])

@tool
def calculate_mortgage(principal: int, rate: float, years: int) -> str:
    """
    Calculate the monthly mortgage payment.
    Args:
        principal: The loan amount (e.g., 500000).
        rate: The annual interest rate in percentage (e.g., 5.0 for 5%).
        years: The loan tenure in years (e.g., 30).
    Returns:
        A string with the monthly payment amount.
    """
    print(f"Calculating mortgage for ${principal} at {rate}% for {years} years...")
    try:
        monthly_rate = rate / 100 / 12
        num_payments = years * 12
        if monthly_rate == 0:
            monthly_payment = principal / num_payments
        else:
            monthly_payment = (principal * monthly_rate) / (1 - (1 + monthly_rate) ** -num_payments)
        return json.dumps({"monthly_payment": f"${monthly_payment:.2f}"})
    except Exception as e:
        return json.dumps({"error": f"Error calculating mortgage: {str(e)}"})

@tool
def search_neighborhood(location: str, query: str) -> str:
    """
    Search for information about a neighborhood (schools, safety, amenities, etc.).
    Args:
        location: The location or neighborhood name.
        query: The specific question about the neighborhood (e.g., "schools", "safety").
    """
    print(f"Searching neighborhood info for {location}: {query}...")
    # search = DuckDuckGoSearchRun()
    # return search.invoke(f"{location} {query}")
    return json.dumps({"info": f"Mock neighborhood info for {location}: {query}. Schools are good, safety is high."})

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

# Define Agent
tools = [search_properties, calculate_mortgage, search_neighborhood]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert Real Estate Agent. Your goal is to help users find properties, "
               "calculate costs, and understand the neighborhood. "
               "Use the available tools to search for properties, calculate mortgages, and find neighborhood info. "
               "Always provide a helpful and comprehensive response."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def main():
    # Complex user request (Targeting Houston for SimplyRETS test data)
    # user_input = "Find me a 3-bed house in Houston under $10,000,000 (use a high budget for test data), calculate the mortgage for 30 years at 5% interest for one of them, and tell me about the schools in that area."
    # user_input = "Find me a 3-bed house in Houston under $10,000,000 and calculate the mortgage for 30 years at 5% interest for one of them."
    # user_input = "Calculate the mortgage for a $500,000 loan at 5% for 30 years."
    user_input = "Calculate the mortgage for a $500,000 loan at 5% for 30 years.."
    print(f"User Request: {user_input}")
    
    result = agent_executor.invoke({"input": user_input})
    
    print("\n--- Agent Response ---")
    print(result['output'])

if __name__ == '__main__':
    main()
