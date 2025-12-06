# 📧 AI-Powered Automatic Email Reply System  
### 🔥 Intelligent Customer Care Automation using RAG + LLMs

This project is a fully AI-driven **automated email responder** built for customer support teams.  
It connects directly to Gmail, reads incoming emails, classifies them, retrieves product knowledge using **RAG + FAISS**, and sends accurate auto-generated replies.

Complaint emails are forwarded to the complaint-handling team, while low-confidence or irrelevant messages are safely ignored.

This system includes:
- A complete **web dashboard**
- **LLM-powered email intelligence**
- **Semantic product search from database**
- **Google OAuth login**
- **Confidence-controlled automatic replies**

---

## 🚀 Features

### 🔹 **AI Email Intelligence**
- Email intent classification  
- Content extraction & summary  
- RAG-enhanced contextual understanding  
- LLM-powered response generation  
- Confidence score for every reply  

> 🛑 **Low confidence replies are NOT sent**  
If the LLM is uncertain, the system logs the email for manual review instead of sending a wrong or risky message.

---

## 🤖 **RAG (Retrieval-Augmented Generation)**

Product information is processed through a custom RAG pipeline:

- Embedded using **Sentence Transformers**
- Stored inside a **FAISS vector database**
- Incoming email → encoded → semantic search → best matching product chunk returned
- Gemini 2.5 Flash generates final reply using retrieved context

### Benefits  
✔️ Highly accurate product-based responses  
✔️ Effective semantic matching even for vague questions  
✔️ Knowledge base easily updatable  
✔️ Scales to thousands of products  

---

## 📬 **Automatic Email Processing Flow**

### ✉️ **1. Product Inquiry Emails**
- Semantic search (FAISS)
- Retrieve relevant product data  
- Generate answer with LLM + RAG
- Send automatic reply **only if confidence is high**
- Log conversation to DB

### ⚠️ **2. Complaint Emails**
- Forward directly to complaint-management team  
- Summary generated for internal context

### 💤 **3. Other / Unrelated Emails**
- Ignored or marked as “Non-actionable”

---

## 📊 Dashboard Features

The dashboard shows:
- Total replied emails  
- Product inquiries handled  
- Complaints received  
- Unread email count  
---

## 🔐 User System
- Login with **Google OAuth**
- Connect Gmail inbox securely
- Revoke access anytime

---

## 🛠️ Technologies Used

### **AI / NLP**
- **Gemini 2.5 Flash**
- **Sentence Transformers**
- **FAISS Vector Store**
- **Custom RAG Pipeline**

### **Backend**
- Python 3.13+  
- FastAPI  
- SQLAlchemy  
- Gmail API  
- OAuthlib  

### **Frontend**
- React.js  
- Vite  
- Axios  

### **Database**
- PostgreSQL  

---

## 📦 Project Capabilities
- End-to-end automation  
- Production-ready Gmail integration  
- Smart decision-making using AI confidence scores  

---



