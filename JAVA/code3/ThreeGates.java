package threegates;

import java.util.Random;
import java.util.Scanner;
/**
 * This program displays a test for 3-gate question .
 * @version 1.0 2018-09-17
 * @author He Yongqiang
 */
public class ThreeGates
{

	public static void main(String[] args)
	{
		double wonRate = 0.0;
		int wonTimes =0;
		int i=0;
		for (i = 0; i < 10; i++)
		{
			int wonGate = new Random().nextInt(3) + 1;

			Scanner in = new Scanner(System.in);
			int yourChoice=0 ;
			do
			{
				System.out.println("Choose a gate, please(1, 2, or 3):");
				yourChoice = in.nextInt();
			} while (yourChoice < 1 || yourChoice > 3);

			System.out.printf("You chose gate %d\n", yourChoice);
//			System.out.println(wonGate);
			if (yourChoice == wonGate)
				wonTimes++;
			
		}
		System.out.println("you won "+ wonTimes +" times.");
		wonRate = (double)wonTimes/i;
		System.out.printf("Your wonRate is %f .", wonRate);
	}

}
