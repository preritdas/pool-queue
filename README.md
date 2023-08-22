# Pool Queue


## To-do

1. Connect Twilio, and implement calling logic to call the next person in the queue and wait for confirmation from the last king, and move to the next person in the queue if the confirmation is not received within a certain time frame.
2. Implement endpoints for inbound text messages, and logic to respond via text.
3. Deploy to GCP.

## Idea

**1. Product Name:**
Pool Queue (Play on words: Pool Cue, Pool Queue)

**2. Product Overview:**
Pool Queue is a mobile application aimed at improving the efficiency of managing queues for practice tables in pool venues. By moving away from traditional, manual queue methods, this app aspires to streamline the process, reducing time consumption, frustration, and awkward situations when the queue is particularly busy.

**3. Problem Statement:**
The current process of managing queues for pool tables is inefficient and frustrating. The lack of a formalized system often leads to confusion about who is next, where the next player is, and whether their spot should be held if they temporarily leave. 

**4. Solution:**
Pool Queue addresses this problem through an automated system that manages queues via a text messaging interface. 

**5. Key Features:**

**5.1 Text-to-Join Queue:**
Users can join the queue through a simple text message. Once it's their turn at the table, they'll receive a phone call notification. 

**5.2 Time-Limited Response:**
After receiving the call, users will have a specific time frame (30-45 seconds, or a configurable parameter) to get to the table and check in for the match.

**5.3 Verification System:**
In order to prevent misuse, the system will verify that the user has made it to the table. The winner of the previous match will be responsible for confirming the arrival of the next player and indicating the start of the new match.

**5.4 Match End Confirmation:**
To prevent potential disputes, the system will rely on the loser of a match to confirm the match's end. This ensures the queue moves forward and reduces chances of two people claiming to be the winner. If a loser fails to confirm, it could stall the queue, incentivizing them and others to ensure prompt confirmation.

**5.5 Override and Reset:**
In case the system fails or falls out of sync, the app will include a feature to override and reset the queue.

**5.6 Visual Queue:**
To ensure transparency and assist in manual calling if needed, the app will provide a visual representation of the queue.

**5.7 Name-Based Registration:**
New users will provide their name when they first text the number. The system will store this name in a database, and it will be used to manage the queue. No user can enter or join the queue without having a name registered.

**6. Critical Assumptions & Risks:**
The app relies on the assumption that users will not misuse the system and will act in good faith. To mitigate this, the system is designed to handle worst-intention scenarios. 

The app's adoption is a potential risk. If it's not user-friendly, reliable, or accurate, users may disregard it and revert to traditional methods. It must be ensured that the app is easy to use and reliable to prevent such scenarios.

**7. Future Enhancements:**
As part of the product's continuous improvement, feedback from users will be crucial. This feedback will guide future enhancements, which could include additional features, improved user experience, and system optimization. 

**8. Conclusion:**
By automating the queue management for pool tables and ensuring a fair and transparent process, Pool Queue aims to improve the pool playing experience, making it less frustrating and more efficient. As this product idea continues to develop, additional features may be introduced to further enhance this experience.