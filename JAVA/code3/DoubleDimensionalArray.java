
public class DoubleDimensionalArray
{

	public static void main(String[] args)
	{
		int[][] iArr;
		iArr= new int[3][];
		int[] a = {1,2,3};
		int[] b = {11,12,13,14};
		int[] c = {21,22,23,24,25};
		iArr[0]=a;
		iArr[1]=b;
		iArr[2]=c;
		System.out.println(iArr[2][3]);
		b[2]=100;
		System.out.println(iArr[1][2]);
	}

}
