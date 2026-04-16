
/**
 * This program displays a test for the bit operations .
 * @version 1.0 2018-09-10
 * @author He Yongqiang
 */
public class Quiz
{
	public static void main(String[] args)
	{
		int student=0;
		student |= 1<<10;
		student |= 1<<15;
		student &= ~(1<<10);
		boolean hasPassed10 = (student & (1<<10))!=0;
		boolean hasPassed15 = (student & (1<<15))!=0;
		System.out.println("student10 has passed the quiz:" + hasPassed10);
		System.out.println("student15 has passed the quiz:" + hasPassed15);
	}
}
