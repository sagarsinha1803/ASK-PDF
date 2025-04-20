from dotenv import load_dotenv
import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    ChatPromptTemplate
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory

from pd_loader import PDFLoader

load_dotenv('./.env')

class LLMCore:
    def __init__(self):
        self.base_url = os.getenv("BASE_URL")
        self.model = os.getenv("MODEL")
        self.connection= os.getenv("CONNECTION_URL")
        self.llm = ChatOllama(base_url=self.base_url, model=self.model)

    def get_session_history(self, session_id):
        message_history = SQLChatMessageHistory(
            connection=self.connection,
            session_id=session_id,
            table_name="chat_message_history_1"
        )
        return message_history

    def _get_runnable_with_history(self, chain):
        runnable_with_history = RunnableWithMessageHistory(
            chain, self.get_session_history, input_messages_key="question", 
            history_messages_key="history"
        )
        return runnable_with_history

    def _setup_template(self):
        sysmsg = SystemMessagePromptTemplate.from_template(
            """
            You are a helpfull AI assitant who answeres user question based on the context provided.
            Do not answere in more than {words} words.
            """
        )
        humanmsg = HumanMessagePromptTemplate.from_template(
            """
            Answer user question based on the provided context only! If you don't know the answer, then say "I don't know".
            ### Context:
            {context}

            ### Question:
            {question}

            ### Answer:"""
        )

        message = [sysmsg, MessagesPlaceholder(variable_name="history"), humanmsg]

        template = ChatPromptTemplate(messages=message)
        return template
    
    def _get_chain(self, template):
        qna_chain = template | self.llm | StrOutputParser()
        return qna_chain
    
    def chat_with_pdf(self, session_id, question, words=50):
        my_pdf = PDFLoader()
        context = my_pdf.get_context()
        template = self._setup_template()
        qna_chain = self._get_chain(template)
        runnable_with_history = self._get_runnable_with_history(qna_chain)
        for output in runnable_with_history.stream(
            {
                'context': context,
                'question': question,
                'words': words
            },
            config={"configurable": {"session_id": session_id}}
        ):
            yield output
