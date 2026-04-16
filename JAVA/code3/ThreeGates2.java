package threegates;

import java.util.Random;
import java.util.Scanner;
/**
 * This program displays a test for 3-gate question .
 * @version 1.0 2018-09-17
 * @author He Yongqiang
 */
public class ThreeGates2
{

	public static void main(String[] args)
	{
		double wonRate = 0.0;
		int wonTimes =0;
		int i=0;
		System.out.println("How many times would you like to play?");
		Scanner in = new Scanner(System.in);
		int playTimes = in.nextInt();
		for (i = 0; i < playTimes; i++)
		{
			int wonGate = new Random().nextInt(3) + 1;
		
			int yourChoice=0 ;
			do
			{
				System.out.println("Choose a gate, please(1, 2, or 3):");
				yourChoice = in.nextInt();
			} while (yourChoice < 1 || yourChoice > 3);

			System.out.printf("You chose gate %d\n", yourChoice);
//			System.out.println(wonGate);
///////////////////////////////////////////////////////////////////////////////			
			System.out.print("I can tell you one empty gate is ");
			int temp = 0;
			switch (wonGate)
			{
			case 1:
				if (yourChoice == 1)
				{
					temp = Math.random() < 0.5 ? 2 : 3;
					System.out.println(temp);
				}
				else if (yourChoice == 2)
					System.out.println(3);
				else
					System.out.println(2);
				break;
			case 2:
				if (yourChoice == 2)
				{
					temp = Math.random() < 0.5 ? 1 : 3;
					System.out.println(temp);
				}
				else if (yourChoice == 1)
					System.out.println(3);
				else
					System.out.println(1);
				break;
			case 3:
				if (yourChoice == 3)
				{
					temp = Math.random() < 0.5 ? 1 : 2;
					System.out.println(temp);
				}
				else if (yourChoice == 1)
					System.out.println(2);
				else
					System.out.println(1);
				break;
			}
			
			System.out.print("Would you like to change your choice? Y/N");	
			String change =in.next();
			if(change.equals("Y")||change.equals("y"))
				yourChoice = in.nextInt();
			System.out.printf("Finaly, you chose gate %d\n", yourChoice);
						
			
			if (yourChoice == wonGate) 
			{
				wonTimes++;
				System.out.println("This time, you won!");
			}
			else
				System.out.println("This time, you lost!");
				
			System.out.println("=========================================");
		}
		System.out.println("You won "+ wonTimes +" times.");
		wonRate = (double)wonTimes/i;
		System.out.printf("Your wonRate is %f .", wonRate);
	}

}
